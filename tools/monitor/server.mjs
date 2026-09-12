#!/usr/bin/env node
/**
 * server — serves the mission-control room and streams what the pipeline is doing.
 *
 *   node tools/monitor/server.mjs                     live, tailing .monitor/events.jsonl
 *   node tools/monitor/server.mjs --replay <file>      replay a recorded run
 *   node tools/monitor/server.mjs --port 4173
 *
 * No dependencies on purpose. A lesson that starts with `npm install` failing
 * in front of a class is a lesson that starts badly.
 */
import { createServer } from 'node:http';
import { readFile, readdir, open, stat, writeFile, mkdir } from 'node:fs/promises';
import { watch, existsSync, readlinkSync, symlinkSync, unlinkSync } from 'node:fs';
import { spawn } from 'node:child_process';
import { randomUUID } from 'node:crypto';
import { homedir } from 'node:os';
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
import { extname, join, resolve, normalize } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = fileURLToPath(new URL('.', import.meta.url));
const ROOT = resolve(HERE, '..', '..');           // tools/monitor -> repo root
const PUBLIC = join(HERE, 'public');
const LOG = join(ROOT, '.monitor', 'events.jsonl');

const argv = process.argv.slice(2);
const flag = (name, fallback) => {
  const i = argv.indexOf(name);
  return i === -1 ? fallback : argv[i + 1];
};
const flagEarly = name => flag(name, null);
const PORT = Number(flag('--port', 4173));
/* Where the student's projects live.
   Keeping them inside the template was wrong: CLAUDE.md says the template stays
   empty, and one clone shared by several projects turns into a pile. The
   workspace is a real directory anywhere on the machine, remembered between
   runs, and `project/` symlinks into it — so every skill that reads
   `project/...` keeps working without knowing any of this happened. */
const CONFIG = join(ROOT, '.monitor', 'config.json');
let PROJECTS = join(ROOT, 'projects');
try {
  const saved = JSON.parse(require('node:fs').readFileSync(CONFIG, 'utf8'));
  if (saved.workspace && require('node:fs').existsSync(saved.workspace)) PROJECTS = saved.workspace;
} catch { /* first run */ }
const wsFlag = flagEarly('--workspace');
if (wsFlag) PROJECTS = resolve(wsFlag);

const ALLOW_RUN = argv.includes('--allow-run');
let running = null;

/* The chat is a conversation, not a series of one-shot commands.
   `/kickoff` asks five questions and ends its turn; without a session to resume,
   the answers arrive at an agent that has never heard the questions. So the
   thread keeps one session id and resumes it every turn. */
let chatSession = null;
const REPLAY = flag('--replay', null);
const SPEED = Number(flag('--speed', 1));

/* ── project.yml ────────────────────────────────────────────────────────────
   Only two things are read out of it: which stage the project is in, and how
   each gate last ruled. A full YAML parser would be a dependency and a lie —
   these are the only shapes that matter, so these are the only ones parsed. */

function readProjectState(text) {
  const stage = (text.match(/^stage:\s*([a-z-]+)/m) || [])[1] || null;

  const gates = [];
  const block = text.split(/^gates:\s*$/m)[1];
  if (block) {
    // Stop at the next top-level key (a line starting in column 0 that is not
    // a comment and not part of the list).
    const body = block.split(/^(?![\s#-])\S/m)[0];
    let current = null;
    for (const line of body.split('\n')) {
      const item = line.match(/^\s*-\s*id:\s*(\S+)/);
      if (item) {
        current = { id: item[1], result: null, attempt: 1, name: null };
        gates.push(current);
        continue;
      }
      if (!current) continue;
      const field = line.match(/^\s+(result|attempt|name|checked):\s*(.+?)\s*$/);
      if (field) {
        const [, key, raw] = field;
        current[key] = key === 'attempt' ? Number(raw) : raw;
      }
    }
  }
  // Later attempts supersede earlier ones — the history stays in the file, but
  // the room shows where each gate actually stands now.
  const latest = new Map();
  for (const g of gates) {
    const prev = latest.get(g.id);
    if (!prev || (g.attempt || 1) >= (prev.attempt || 1)) latest.set(g.id, g);
  }
  return { stage, gates: [...latest.values()].sort((a, b) => a.id.localeCompare(b.id)) };
}

/** Every project on disk, not just the one `project/` points at — two sessions
 *  can be working on two of them at the same time, and the room has to be able
 *  to show either without being restarted. */
async function allProjects() {
  let codes = [];
  try {
    codes = (await readdir(PROJECTS, { withFileTypes: true }))
      .filter(d => d.isDirectory() && !d.name.startsWith('.'))
      .map(d => d.name);
  } catch { /* no projects yet */ }

  const out = {};
  for (const code of codes) {
    try {
      const text = await readFile(join(PROJECTS, code, 'project.yml'), 'utf8');
      const st = readProjectState(text);
      st.name = (text.match(/^\s{2}name:\s*(.+?)\s*(?:#.*)?$/m) || [])[1] ?? code;
      out[code] = st;
    } catch {
      out[code] = { stage: null, gates: [], name: code };
    }
  }
  return out;
}

/** Repoint `project/` at one project inside the workspace. Absolute, because
 *  the workspace can be anywhere on the machine. */
/** Run a command and resolve only if it succeeded. */
function run(cmd, args, cwd) {
  return new Promise((ok, fail) => {
    const child = spawn(cmd, args, { cwd, stdio: ['ignore', 'ignore', 'pipe'] });
    let err = '';
    child.stderr?.on('data', d => err += d);
    child.on('error', fail);
    child.on('exit', c => c === 0 ? ok() : fail(new Error(err.trim().split('\n')[0] || `${cmd} exit ${c}`)));
  });
}

function pointAt(code) {
  const link = join(ROOT, 'project');
  try { if (existsSync(link)) unlinkSync(link); } catch { /* ignore */ }
  symlinkSync(join(PROJECTS, code), link);
}

function activeCode() {
  try {
    const link = join(ROOT, 'project');
    if (existsSync(link)) return readlinkSync(link).replace(/\/$/, '').split('/').pop();
  } catch { /* not a symlink */ }
  try { return require('node:fs').readFileSync(join(PROJECTS, '.active'), 'utf8').trim(); }
  catch { return null; }
}

/* ── event stream ─────────────────────────────────────────────────────────── */

const clients = new Set();

function push(type, data) {
  const frame = `event: ${type}\ndata: ${JSON.stringify(data)}\n\n`;
  for (const res of clients) {
    try { res.write(frame); } catch { clients.delete(res); }
  }
}

/** Follow the append-only log. Handles the file not existing yet, and being
 *  truncated (which is what `/monitor --reset` does between demos). */
async function tailLog() {
  let offset = 0;
  let carry = '';

  const drain = async () => {
    let handle;
    try {
      const info = await stat(LOG);
      if (info.size < offset) { offset = 0; carry = ''; }   // truncated
      if (info.size === offset) return;
      handle = await open(LOG, 'r');
      const length = info.size - offset;
      const buffer = Buffer.alloc(length);
      await handle.read(buffer, 0, length, offset);
      offset = info.size;
      carry += buffer.toString('utf8');
      const lines = carry.split('\n');
      carry = lines.pop() ?? '';
      for (const line of lines) {
        if (!line.trim()) continue;
        try { push('hook', JSON.parse(line)); } catch { /* half-written line */ }
      }
    } catch {
      // no log yet — nothing has run since the last reset
    } finally {
      await handle?.close();
    }
  };

  await drain();
  // fs.watch misses appends on some filesystems; the poll is the honest one.
  setInterval(drain, 350);
  try { watch(join(ROOT, '.monitor'), () => drain()); } catch { /* dir may not exist */ }
}

/* Replay transport. The room is something a teacher stands in front of, so it
   has to be pausable, rewindable and slowable — a demo that can only run at one
   speed from the top is a video, not a teaching aid. */
const transport = { paused: false, speed: SPEED, restart: false, playing: false };

const gate = () => new Promise(resolve => {
  const check = () => transport.paused ? setTimeout(check, 120) : resolve();
  check();
});

async function replayLog(file) {
  const path = resolve(ROOT, file);
  const lines = (await readFile(path, 'utf8')).split('\n').filter(l => l.trim());
  const events = lines.map(l => { try { return JSON.parse(l); } catch { return null; } })
                      .filter(Boolean);
  console.log(`  replaying ${events.length} events from ${file} at ${SPEED}x`);

  const run = async () => {
    transport.playing = true;
    transport.restart = false;
    push('reset', {});
    push('transport', transport);
    let previous = events[0]?.ts ?? 0;
    for (const event of events) {
      if (transport.restart) return run();
      const gap = Math.min(Math.max((event.ts - previous) * 1000, 120), 2600) / transport.speed;
      previous = event.ts;
      await gate();
      await new Promise(r => setTimeout(r, gap));
      if (transport.restart) return run();
      push('hook', event);
    }
    transport.playing = false;
    push('transport', transport);
    setTimeout(() => { if (!transport.paused) run(); }, 6000 / transport.speed);
  };
  run();
}

/* ── http ───────────────────────────────────────────────────────────────────*/

const TYPES = {
  '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8', '.json': 'application/json; charset=utf-8',
  '.png': 'image/png', '.jpg': 'image/jpeg', '.svg': 'image/svg+xml',
};

const server = createServer(async (req, res) => {
  const url = new URL(req.url, 'http://localhost');

  if (url.pathname === '/events') {
    res.writeHead(200, {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      Connection: 'keep-alive',
    });
    res.write(': connected\n\n');

    // Catch the new client up. Without this, opening the page during a run
    // shows an empty room because the stream only carries what happens next —
    // which is exactly when someone is most likely to open it.
    if (!REPLAY) {
      try {
        const past = (await readFile(LOG, 'utf8')).split('\n').filter(l => l.trim()).slice(-300);
        for (const line of past) {
          try {
            JSON.parse(line);
            res.write(`event: hook\ndata: ${line}\n\n`);
          } catch { /* half-written line */ }
        }
      } catch { /* nothing has run yet */ }
    }

    clients.add(res);
    const beat = setInterval(() => { try { res.write(': beat\n\n'); } catch {} }, 15000);
    req.on('close', () => { clearInterval(beat); clients.delete(res); });
    return;
  }

  if (url.pathname === '/dirs') {
    // Read-only directory listing so the entrance can offer a real path.
    // The File System Access API hands back a handle, not a path, and a path is
    // exactly what a symlink and a shell script need.
    const want = url.searchParams.get('path') || homedir();
    let here = resolve(want);
    let entries = [];
    try {
      entries = (await readdir(here, { withFileTypes: true }))
        .filter(d => d.isDirectory() && !d.name.startsWith('.'))
        .map(d => d.name)
        .sort((a, b) => a.localeCompare(b))
        .slice(0, 400);
    } catch {
      here = homedir();
      try {
        entries = (await readdir(here, { withFileTypes: true }))
          .filter(d => d.isDirectory() && !d.name.startsWith('.')).map(d => d.name).sort();
      } catch { entries = []; }
    }
    res.writeHead(200, { 'Content-Type': TYPES['.json'] });
    res.end(JSON.stringify({
      here,
      parent: here === '/' ? null : join(here, '..'),
      home: homedir(),
      entries,
      current: PROJECTS,
    }));
    return;
  }

  if (url.pathname === '/usage') {
    /* What a run cost, read from the transcript Claude Code already writes.
       Every assistant message carries its own usage block, so the total is a
       sum of things that actually happened rather than an estimate. */
    const sid = (url.searchParams.get('session') || '').replace(/[^A-Za-z0-9-]/g, '');
    const slug = ROOT.replace(/\//g, '-');
    const file = join(homedir(), '.claude', 'projects', slug, `${sid}.jsonl`);
    const total = { input: 0, output: 0, cacheRead: 0, cacheWrite: 0, turns: 0 };
    if (sid) {
      try {
        for (const line of (await readFile(file, 'utf8')).split('\n')) {
          if (!line.trim()) continue;
          let row; try { row = JSON.parse(line); } catch { continue; }
          const u = row?.message?.usage;
          if (!u) continue;
          total.input      += u.input_tokens ?? 0;
          total.output     += u.output_tokens ?? 0;
          total.cacheRead  += u.cache_read_input_tokens ?? 0;
          total.cacheWrite += u.cache_creation_input_tokens ?? 0;
          total.turns += 1;
        }
      } catch { /* session not on disk yet */ }
    }
    total.billable = total.input + total.output + total.cacheWrite;
    res.writeHead(200, { 'Content-Type': TYPES['.json'] });
    res.end(JSON.stringify(total));
    return;
  }

  if (url.pathname === '/state') {
    const [projects, roster] = await Promise.all([
      allProjects(),
      readFile(join(HERE, 'roster.json'), 'utf8').then(JSON.parse).catch(() => null),
    ]);
    const active = activeCode();
    res.writeHead(200, { 'Content-Type': TYPES['.json'] });
    res.end(JSON.stringify({
      projects, active, roster,
      project: projects[active] ?? { stage: null, gates: [] },
      mode: REPLAY ? 'replay' : 'live',
      transport, canRun: ALLOW_RUN, workspace: PROJECTS,
    }));
    return;
  }

  if (url.pathname === '/control' && req.method === 'POST') {
    const body = await new Promise(r => { let b = ''; req.on('data', c => b += c); req.on('end', () => r(b)); });
    let cmd = {};
    try { cmd = JSON.parse(body || '{}'); } catch { /* ignore */ }
    const reply = v => { res.writeHead(200, { 'Content-Type': TYPES['.json'] }); res.end(JSON.stringify(v)); };

    switch (cmd.action) {
      case 'pause':   transport.paused = true;  push('transport', transport); return reply(transport);
      case 'play':    transport.paused = false; push('transport', transport); return reply(transport);
      case 'restart': transport.restart = true; transport.paused = false; push('transport', transport); return reply(transport);
      case 'speed':
        transport.speed = Math.min(4, Math.max(0.25, Number(cmd.value) || 1));
        push('transport', transport);
        return reply(transport);

      case 'switch': {
        // Switching repoints `project/`, which is the path every skill and
        // command in the template already uses — so nothing else has to know
        // that more than one project exists.
        const code = String(cmd.code || '').replace(/[^A-Za-z0-9_-]/g, '');
        if (!code || !existsSync(join(PROJECTS, code))) return reply({ error: 'ไม่พบโปรเจกต์' });
        pointAt(code);
        await writeFile(join(PROJECTS, '.active'), code + '\n');
        push('project', (await allProjects())[code]);
        push('active', { code });
        return reply({ active: code });
      }

      case 'create': {
        // Scaffold only. The template's comments explain what every field wants,
        // and `project-intake` fills them by asking — a blank that says what it
        // needs is worth more than a file pre-filled with plausible guesses.
        const code = String(cmd.code || '').toUpperCase().replace(/[^A-Z0-9]/g, '').slice(0, 6);
        const name = String(cmd.name || '').trim();
        if (!/^[A-Z0-9]{2,6}$/.test(code)) return reply({ error: 'รหัสต้องเป็น A-Z หรือ 0-9 ยาว 2-6 ตัว' });
        if (!name) return reply({ error: 'ต้องมีชื่อโครงการ' });
        const dir = join(PROJECTS, code);
        if (existsSync(dir)) return reply({ error: `มีโปรเจกต์ ${code} อยู่แล้ว` });

        const tpl = join(ROOT, '.claude', 'skills', 'project-intake', 'assets', 'project.yml.template');
        let yml;
        try { yml = await readFile(tpl, 'utf8'); }
        catch { return reply({ error: 'ไม่พบเทมเพลต project.yml' }); }

        const today = new Date().toISOString().slice(0, 10);
        const TBD = 'TBD — ต้องการ [คน/ข้อมูล]';
        const one = v => String(v ?? '').replace(/\s+/g, ' ').trim();

        // Filling five known fields is string substitution, not judgement — it
        // does not need a model, and a form that answers instantly beats one
        // that waits thirty seconds for an agent to type the same thing.
        // Anything left blank becomes TBD, never a plausible-sounding guess.
        const open = [];

        /* Every line in the template carries a trailing comment explaining what
           the field wants — `  name:      # ชื่อโครงการ`. The comment is the
           reason the template is worth keeping, so the value is inserted before
           it and the comment is put back, rather than matching to end-of-line
           and silently writing nothing (which is what the first version did). */
        const put = (key, value) => {
          const re = new RegExp(`^(\\s{2}${key}:)([^\\S\\n]*)(#.*)?$`, 'm');
          if (!re.test(yml)) return false;
          yml = yml.replace(re, (_m, head, _gap, comment) =>
            `${head} ${value}${comment ? '   ' + comment : ''}`);
          return true;
        };
        const field = (key, value, question) => {
          const v = one(value);
          if (!v) open.push(question);
          put(key, v || TBD);
        };

        put('name', name);
        put('code', code);
        put('started', today);
        if (cmd.owner) put('owner', one(cmd.owner));

        field('statement',        cmd.problem, 'ปัญหาในหนึ่งประโยคคืออะไร');
        field('users',            cmd.users,   'ใครเจอปัญหานี้ เจาะจงกว่าคำว่าผู้ใช้');
        field('today_workaround', cmd.today,   'วันนี้เขาทำยังไงเมื่อยังไม่มีของชิ้นนี้');
        field('days_available',   cmd.days,    'มีเวลากี่วันทำงาน');

        // The stack is a decision, so it is recorded as one. Anything left on
        // "ยังไม่ตัดสินใจ" stays an open question rather than becoming a default
        // that nobody chose and everybody later has to live with.
        const picked = [cmd.framework, cmd.styling, cmd.database].map(one).filter(Boolean);
        if (picked.length) {
          put('stack', picked.join(' · '));
        } else {
          put('stack', TBD);
          open.push('จะใช้เฟรมเวิร์ก สไตล์ และฐานข้อมูลอะไร');
        }
        if (!one(cmd.framework)) open.push('ยังไม่ได้เลือกเฟรมเวิร์ก');
        if (!one(cmd.database))  open.push('ยังไม่ได้เลือกฐานข้อมูล');

        if (open.length) {
          const list = open.map(q => `  - text: ${q}\n    raised: ${today}`).join('\n');
          yml = yml.replace(/^open_questions:.*$/m, `open_questions:\n${list}`);
        }

        for (const sub of ['1-product','2-analysis','3-design','4-build','5-quality','6-release'])
          await mkdir(join(dir, sub), { recursive: true });
        await writeFile(join(dir, 'project.yml'), yml);

        // git, when asked for. A project the student will actually push needs
        // to be a repository from the first commit, not converted into one
        // after the history that mattered has already happened.
        let git = null;
        if (cmd.git === 'init' || cmd.git === 'remote') {
          try {
            await writeFile(join(dir, '.gitignore'),
              ['node_modules/', 'dist/', '.DS_Store', '*.pdf', '*.docx', ''].join('\n'));
            await run('git', ['init', '-q'], dir);
            await run('git', ['add', '-A'], dir);
            await run('git', ['-c', 'commit.gpgsign=false', 'commit', '-q', '-m',
                              `เปิดโครงการ ${code} — ${name}`], dir);
            git = 'init';
            const remote = one(cmd.remote);
            if (cmd.git === 'remote' && remote) {
              await run('git', ['remote', 'add', 'origin', remote], dir);
              git = 'remote';
            }
          } catch (e) {
            git = 'failed: ' + e.message;
          }
        }

        pointAt(code);
        await writeFile(join(PROJECTS, '.active'), code + '\n');

        // history, appended not rewritten — a project that was abandoned is
        // still a project that happened
        const index = join(PROJECTS, 'INDEX.md');
        const head = '# ประวัติโปรเจกต์\n\n| รหัส | ชื่อ | เปิดเมื่อ | ระยะล่าสุด |\n|---|---|---|---|\n';
        let idx = '';
        try { idx = await readFile(index, 'utf8'); } catch { idx = head; }
        await writeFile(index, idx.trimEnd() + `\n| ${code} | ${name} | ${today} | intake |\n`);

        push('projects', await allProjects());
        push('active', { code });
        return reply({ code, active: code, open: open.length, git });
      }

      case 'run': {
        if (!ALLOW_RUN) return reply({ error: 'ปิดการสั่งงานจากหน้าเว็บ · เปิดด้วย --allow-run' });
        if (running) return reply({ error: 'กำลังรันอยู่แล้ว' });
        // pipeline.sh, not auto.sh: handing the whole run to one autonomous
        // orchestrator burned its budget reading the repository twice without
        // reaching a single role. The shell holds the stage order instead.
        const args = [join(ROOT, 'tools', 'pipeline.sh'), String(cmd.stage || 'all')];
        // detached so the whole process group can be signalled — killing the
        // shell alone leaves node and claude running, which the first version did
        running = spawn('bash', args, { cwd: ROOT, stdio: 'ignore', detached: true });
        running.unref();
        push('run', { state: 'started', stage: cmd.stage || 'all' });
        running.on('exit', code => { running = null; push('run', { state: 'ended', code }); });
        return reply({ started: true, stage: cmd.stage || 'all' });
      }

      case 'say': {
        // The brief arrives here. Everything the crew does afterwards is a
        // consequence of this text, so it is passed through verbatim — no
        // rewriting, no "helpful" expansion.
        if (!ALLOW_RUN) return reply({ error: 'ปิดการสั่งงานจากหน้าเว็บ · เปิดด้วย --allow-run' });
        if (running) return reply({ error: 'กำลังทำงานอยู่ · รอให้จบหรือกดหยุดก่อน' });
        const text = String(cmd.text || '').trim();
        if (!text) return reply({ error: 'ยังไม่ได้พิมพ์อะไร' });

        push('chat', { who: 'you', text });

        const args = ['-p', text, '--permission-mode', 'acceptEdits'];
        // Same reason as tools/auto.sh: the project is reached through a
        // symlink into the workspace, and without granting it the run stops on
        // a permission prompt that headless mode can never answer.
        args.push('--add-dir', PROJECTS);
        if (chatSession) {
          args.push('--resume', chatSession);
        } else {
          chatSession = randomUUID();
          args.push('--session-id', chatSession);
        }
        running = spawn('claude', args, { cwd: ROOT, detached: true });
        push('run', { state: 'started', brief: text, session: chatSession });

        let buffered = '';
        const emit = chunk => {
          buffered += chunk.toString();
          const lines = buffered.split('\n');
          buffered = lines.pop() ?? '';
          for (const line of lines) if (line.trim()) push('chat', { who: 'crew', text: line });
        };
        running.stdout?.on('data', emit);
        running.stderr?.on('data', emit);
        running.on('exit', code => {
          if (buffered.trim()) push('chat', { who: 'crew', text: buffered });
          running = null;
          push('run', { state: 'ended', code });
        });
        return reply({ sent: true });
      }

      case 'pickdir': {
        // The real Finder dialog. A web page cannot be given a filesystem path
        // by the browser's own picker — it gets a handle — but the server is on
        // this machine, so it can open the native chooser and read the path back.
        if (process.platform !== 'darwin') return reply({ error: 'ตัวเลือกโฟลเดอร์แบบ native ใช้ได้เฉพาะ macOS' });
        const script = `POSIX path of (choose folder with prompt "เลือกโฟลเดอร์สำหรับเก็บโปรเจกต์" default location POSIX file ${JSON.stringify(PROJECTS)})`;
        const picked = await new Promise(resolve => {
          const child = spawn('osascript', ['-e', script], { stdio: ['ignore', 'pipe', 'pipe'] });
          let out = '', err = '';
          child.stdout.on('data', d => out += d);
          child.stderr.on('data', d => err += d);
          child.on('error', () => resolve(null));
          child.on('exit', code => resolve(code === 0 ? out.trim() : null));
        });
        if (!picked) return reply({ cancelled: true });
        return reply({ path: picked.replace(/\/$/, '') });
      }

      case 'workspace': {
        const want = resolve(String(cmd.path || ''));
        if (!want || !existsSync(want)) return reply({ error: 'ไม่พบโฟลเดอร์นี้' });
        try {
          await mkdir(want, { recursive: true });
          await mkdir(join(ROOT, '.monitor'), { recursive: true });
          await writeFile(CONFIG, JSON.stringify({ workspace: want }, null, 2) + '\n');
        } catch (e) {
          return reply({ error: 'เขียนค่าไม่ได้: ' + e.message });
        }
        PROJECTS = want;
        const found = await allProjects();
        push('projects', found);
        return reply({ workspace: PROJECTS, projects: Object.keys(found) });
      }

      case 'newchat': {
        chatSession = null;
        push('chat', { who: 'crew', text: '— เริ่มบทสนทนาใหม่ (ตัวก่อนหน้าถูกลืมแล้ว) —' });
        return reply({ reset: true });
      }

      case 'stop': {
        if (running) {
          try { process.kill(-running.pid, 'SIGTERM'); } catch { try { running.kill(); } catch {} }
          running = null;
          push('run', { state: 'stopped' });
          return reply({ stopped: true });
        }
        // A run started from a shell has no child handle here, but the stop
        // button is on screen for it too — so stop it by name rather than
        // showing a control that quietly does nothing.
        return new Promise(done => {
          const killer = spawn('pkill', ['-f', 'tools/pipeline.sh']);
          killer.on('exit', c => {
            spawn('pkill', ['-f', 'claude -p']);
            push('run', { state: 'stopped' });
            done(reply({ stopped: c === 0, external: true }));
          });
        });
      }
    }
    return reply({ error: 'ไม่รู้จักคำสั่งนี้' });
  }

  // static — confined to public/
  const wanted = url.pathname === '/' ? '/index.html' : url.pathname;
  const target = join(PUBLIC, normalize(wanted).replace(/^(\.\.[/\\])+/, ''));
  if (!target.startsWith(PUBLIC)) { res.writeHead(403).end('no'); return; }
  try {
    const body = await readFile(target);
    res.writeHead(200, { 'Content-Type': TYPES[extname(target)] || 'application/octet-stream' });
    res.end(body);
  } catch {
    res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
    res.end('404');
  }
});

server.listen(PORT, '127.0.0.1', () => {
  console.log('\n  design-lazyyy mission control');
  console.log(`  ▶ http://localhost:${PORT}`);
  console.log(`  ▶ ${REPLAY ? `replay ${REPLAY}` : `watching ${LOG.replace(ROOT + '/', '')}`}`);
  console.log(`  ▶ โปรเจกต์อยู่ที่ ${PROJECTS}`);
  console.log(`  ▶ สั่งงานจากหน้าเว็บ: ${ALLOW_RUN ? 'เปิด' : 'ปิด (ใส่ --allow-run เพื่อเปิด)'}\n`);
});

if (REPLAY) replayLog(REPLAY); else tailLog();

// A gate ruling rewrites project.yml, so the room reflects it without a reload.
try {
  watch(PROJECTS, { recursive: true }, async (_e, name) => {
    if (name && name.endsWith('project.yml')) push('projects', await allProjects());
  });
} catch { /* no projects yet */ }
