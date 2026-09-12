/**
 * app — turns the hook stream into a room.
 *
 * Nothing here invents activity. Every light that comes on is a `SubagentStart`
 * that actually fired, every filename on a screen came out of a real
 * `tool_input.file_path`, and the verdict card only changes when the correcter
 * actually ran. If the room looks idle, the pipeline is idle.
 */
import { Sound } from './sound.js';

const $ = s => document.querySelector(s);
const cast = $('#cast');
const feed = $('#feed');
const wires = $('#wires');

const CENTRE = { x: 50, y: 60 };

/* Score is a tally of things that actually happened. XP is tool calls, a level
   is finished handoffs, the streak is consecutive PASS verdicts from the
   correcter. None of it is invented — if the room is quiet, the score is too. */
const game = { xp: 0, acts: 0, handoffs: 0, streak: 0, best: 0, unlocked: new Set() };
const state = { stations: [], byId: new Map(), byAgent: new Map(), roster: null };

/* ── boot ───────────────────────────────────────────────────────────────── */

const res = await fetch('/state');
const boot = await res.json();
const { project, projects, active, roster, mode, transport, canRun, workspace } = boot;
state.roster = roster;
state.projects = projects ?? {};
state.active = active;
state.workspace = workspace;

$('#mode').textContent = mode === 'replay' ? 'เล่นซ้ำ' : 'สด';
$('#mode').className = 'chip ' + mode;

// The room art is optional — the CSS gradient set is a real fallback, not a
// broken-image placeholder, so a fresh clone with no art still teaches.
for (const candidate of ['art/room-empty.png', 'art/room-bg.png']) {
  if (await exists(candidate)) {
    $('#room').style.setProperty('--art', `url(${candidate})`);
    $('#room').classList.add('has-art');
    break;
  }
}
async function exists(url) {
  try { return (await fetch(url, { method: 'HEAD' })).ok; } catch { return false; }
}

buildCast();
applyProject(project);
scoreboard();
buildTabs();
wireControls(transport, canRun, mode);
wireChat(canRun);
buildPicker();
$('#ws-path').textContent = state.workspace ?? '—';

/* ── the cast ───────────────────────────────────────────────────────────── */

function buildCast() {
  const painted = state.roster?.stations ?? [];   // desks that exist in the art
  const drawn   = state.roster?.extra ?? [];      // desks the room has to grow
  const all = [...painted, ...drawn.map(p => ({ ...p, drawDesk: true }))];
  for (const p of all) {
    const el = document.createElement('div');
    el.className = 'station';
    el.dataset.id = p.id;
    el.style.cssText = `left:${p.x}%; top:${p.y}%; --tint:${p.color}`;
    // A panel above a back-row desk collides with the HUD, and a panel that
    // hangs off the side of a corner desk collides with the window. Both are
    // decided here, once, from the desk's own position.
    el.dataset.row = p.y < 60 ? 'back' : 'front';
    el.dataset.panel = p.y < 60 ? 'below' : 'above';
    el.dataset.side = p.x < 22 ? 'left' : p.x > 78 ? 'right' : 'centre';
    el.innerHTML = `
      <div class="holo">
        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="${p.glyph ?? 'M4 12h16'}"/></svg>
        <b>${p.name}</b>
        <u>${p.title ?? p.role ?? ''}</u>
        <div class="bars"><i></i><i></i><i></i><i></i><i></i><i></i></div>
        <div class="scan"></div>
      </div>
      <div class="screen">
        <em>${p.role ?? ''}</em>
        <p class="what">พร้อมรับงาน</p>
        <p class="msg"></p>
        <div class="bar"><i></i></div>
        <div class="count"><span class="acts">ลงมือ 0 ครั้ง</span><span class="clock">—</span></div>
      </div>
      <div class="figure">
        <div class="sprite"></div>
        <div class="shade"></div>
        <div class="pad"></div>
      </div>
      <div class="plate">
        <b>${p.name}</b>
        <i class="rank">${p.title ?? ''}</i>
        <span>${p.th ?? ''}</span>
      </div>
      <div class="xp"><i></i></div>`;
    cast.appendChild(el);

    const station = { ...p, el, home: { x: p.x, y: p.y }, acts: 0, since: 0, timer: null };
    state.stations.push(station);
    state.byId.set(p.id, station);
    if (!state.byAgent.has(p.agent)) state.byAgent.set(p.agent, []);
    state.byAgent.get(p.agent).push(station);

    // Art is per-station and optional; a station with none keeps the neon pad.
    const art = `art/crew-${p.id}.png`;
    exists(art).then(ok => { if (ok) el.querySelector('.sprite').style.backgroundImage = `url(${art})`; });
    exists(`art/walk-${p.id}.png`).then(ok => {
      if (!ok) return;
      el.querySelector('.sprite').style.backgroundImage = `url(art/walk-${p.id}.png)`;
      el.dataset.frames = '2';
    });
  }
}

/** A role can own more than one station — `developer` builds both the client
 *  and the server, and which desk lights up is decided by the path it writes,
 *  not by a guess. */
function resolve(agent, path) {
  const options = state.byAgent.get(agent);
  if (!options?.length) return null;
  if (options.length === 1) return options[0];
  if (path) {
    const hit = options.find(o => o.pathPrefix && path.startsWith(o.pathPrefix));
    if (hit) return hit;
  }
  return options.find(o => o.el.classList.contains('busy')) ?? options[0];
}

/* ── choreography ───────────────────────────────────────────────────────── */

const sleep = ms => new Promise(r => setTimeout(r, ms));

function wire(from, to, colour, bend = -14) {
  const r = wires.getBoundingClientRect();
  const x1 = r.width * from.x / 100, y1 = r.height * from.y / 100 - 90;
  const x2 = r.width * to.x / 100,   y2 = r.height * to.y / 100 - 90;
  const mx = (x1 + x2) / 2, my = (y1 + y2) / 2 + bend * 3;

  const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
  path.setAttribute('d', `M${x1},${y1} Q${mx},${my} ${x2},${y2}`);
  path.setAttribute('stroke', colour);
  path.style.color = colour;
  const len = Math.hypot(x2 - x1, y2 - y1) * 1.25;
  path.style.strokeDasharray = `${len * .3} ${len}`;
  path.style.strokeDashoffset = len * .3;
  wires.appendChild(path);
  path.animate(
    [{ strokeDashoffset: len * .3, opacity: 0 },
     { opacity: 1, offset: .25 },
     { strokeDashoffset: -len, opacity: 0 }],
    { duration: 900, easing: 'cubic-bezier(.3,.7,.4,1)' }
  ).onfinish = () => path.remove();
}

/** Walk there, then back. Footsteps are timed to the gait so the sound and the
 *  animation are the same event rather than two things that drift apart. */
async function walk(station, dest) {
  const el = station.el;
  const from = parseFloat(el.style.left);
  el.classList.toggle('facing-left', dest.x < from);
  el.classList.add('walking');
  el.style.left = dest.x + '%';
  el.style.top = dest.y + '%';

  let right = false;
  const steps = setInterval(() => { Sound.step(right = !right); }, 260);
  await sleep(2400);
  clearInterval(steps);
  el.classList.remove('walking');
}

async function dispatch(station) {
  const el = station.el;
  if (el.classList.contains('busy')) return;

  $('#core').classList.add('busy');
  wire(CENTRE, station.home, station.color);
  Sound.dispatch();
  await sleep(420);

  el.classList.add('awake', 'busy');
  focus(station);
  dock();
  station.acts = 0;
  station.since = Date.now();
  paint(station, 'ได้รับคำสั่ง');
  Sound.wake();
  tickClock(station);

  // step out to take the order, then back to the desk to do the work
  const side = station.home.x < 50 ? -12 : 12;
  await walk(station, { x: CENTRE.x + side, y: CENTRE.y });
  await sleep(300);
  await walk(station, station.home);
}

/** Everything running right now, as a list. Laid out, so it cannot collide. */
function dock() {
  const busy = state.stations.filter(s => s.el.classList.contains('busy'));
  const el = $('#dock');
  el.innerHTML = busy.map(s => {
    const secs = s.since ? Math.floor((Date.now() - s.since) / 1000) : 0;
    const clock = `${String(Math.floor(secs / 60)).padStart(2,'0')}:${String(secs % 60).padStart(2,'0')}`;
    const what = s.el.querySelector('.what').textContent;
    return `<div class="row" style="--tone:${s.color}"><i></i>
      <div><b>${s.name}</b><span>${escape(what)}</span></div>
      <em>${clock}<u>${s.acts} ครั้ง</u></em></div>`;
  }).join('');
}
setInterval(dock, 1000);

/* Token cost of the current run. Students ask what a pipeline run costs, and a
   number nobody can see is a number nobody learns from. */
let watchedSession = null;

const compact = n =>
  n >= 1e6 ? (n / 1e6).toFixed(2) + 'M' :
  n >= 1e3 ? (n / 1e3).toFixed(1) + 'k' : String(n);

function brand() {
  const p = state.projects?.[state.active];
  const name = p ? `${state.active} · ${p.name ?? ''}` : '—';
  const u = state.usage;
  const cost = u && u.turns
    ? `<u class="${state.running ? 'live' : ''}">${compact(u.billable)} tokens · ${u.turns} เทิร์น</u>`
    : '';
  $('#projname').innerHTML = `<b>${escape(name)}</b>${cost}`;
}

async function pollUsage() {
  if (!watchedSession) return;
  try {
    state.usage = await fetch('/usage?session=' + encodeURIComponent(watchedSession)).then(r => r.json());
    brand();
  } catch { /* server restarting */ }
}
setInterval(pollUsage, 4000);

function scoreboard() {
  $('#sxp').textContent = game.xp.toLocaleString('th-TH');
  $('#slv').textContent = 1 + Math.floor(game.handoffs / 2);
  $('#sst').textContent = game.streak;
  $('#sac').textContent = game.acts;
  $('#streakbox').classList.toggle('hot', game.streak >= 3);
}

function award(station, amount, why) {
  game.xp += amount;
  station.xp = (station.xp ?? 0) + amount;
  // The title on the plate is the role's seniority, not a score — this crew is
  // eleven specialists, and a specialist does not level up out of being one.
  // XP still counts; it fills the bar, it does not rename anybody.
  station.el.querySelector('.xp i').style.width = `${Math.min(100, (station.xp % 400) / 4)}%`;

  const pop = document.createElement('div');
  pop.className = 'pop';
  pop.textContent = `+${amount}`;
  // Outside .figure on purpose: the figure is mirrored with scaleX(-1) when the
  // character walks left, and anything inside it gets mirrored too — which is
  // right for a person and wrong for a number.
  station.el.appendChild(pop);
  setTimeout(() => pop.remove(), 1200);

  if (why) toast(why, station.name, station.color);
  scoreboard();
}

function toast(kind, text, tone) {
  const el = document.createElement('div');
  el.className = 'toast';
  el.style.setProperty('--tone', tone ?? '#7DD3FC');
  el.innerHTML = `<em>${kind}</em><strong>${escape(text)}</strong>`;
  $('#toasts').appendChild(el);
  setTimeout(() => el.remove(), 4400);
}

function once(key, kind, text, tone) {
  if (game.unlocked.has(key)) return;
  game.unlocked.add(key);
  toast(kind, text, tone);
}

/* Panels are placed from each desk's own position, which is right until two
   desks sit close enough that their cards touch. Rather than hand-tuning
   coordinates — which breaks again the moment someone adds a role to
   roster.json — overlapping cards are pushed apart here, after layout, every
   time the set of visible cards changes. */
let deconflicting = false;
function deconflict() {
  if (deconflicting) return;
  deconflicting = true;
  requestAnimationFrame(() => {
    deconflicting = false;
    const cards = [...document.querySelectorAll('.station.awake .screen')];
    for (const c of cards) c.style.setProperty('--nudge', '0px');
    if (cards.length < 2) return;

    // resolve top-down so a pushed card never lands back on the one above it
    const boxed = cards
      .map(el => ({ el, r: el.getBoundingClientRect(), down: el.closest('.station').dataset.panel === 'below' }))
      .sort((a, b) => a.r.top - b.r.top);

    for (let i = 0; i < boxed.length; i++) {
      for (let j = i + 1; j < boxed.length; j++) {
        const a = boxed[i].r, b = boxed[j].r;
        const hit = a.left < b.right && b.left < a.right && a.top < b.bottom && b.top < a.bottom;
        if (!hit) continue;
        const shift = a.bottom - b.top + 10;
        const dir = boxed[j].down ? shift : -shift;
        const was = parseFloat(boxed[j].el.style.getPropertyValue('--nudge')) || 0;
        boxed[j].el.style.setProperty('--nudge', `${was + dir}px`);
        boxed[j].r = new DOMRect(b.x, b.y + (boxed[j].down ? shift : -shift), b.width, b.height);
      }
    }
  });
}

/** Only the desk that moved last shows its card. */
function focus(station) {
  for (const s of state.stations) s.el.classList.toggle('focus', s === station);
}

function paint(station, text) {
  station.el.querySelector('.what').textContent = text;
  focus(station);
  dock();
  station.el.querySelector('.acts').textContent = `ลงมือ ${station.acts} ครั้ง`;
}

function tickClock(station) {
  clearInterval(station.timer);
  station.timer = setInterval(() => {
    if (!station.since) return;
    const s = Math.floor((Date.now() - station.since) / 1000);
    station.el.querySelector('.clock').textContent =
      `${String(Math.floor(s / 60)).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`;
  }, 1000);
}

/** One panel per desk. The closing line replaces the activity line rather than
 *  floating a second box over it — two boxes per desk is what made eight desks
 *  unreadable. */
function say(station, text) {
  const el = station.el;
  const msg = el.querySelector('.msg');
  msg.textContent = text;
  el.classList.add('speaking');
  focus(station);
  clearTimeout(msg._t);
  msg._t = setTimeout(() => el.classList.remove('speaking'), 5000);
}

function finish(station, text) {
  const el = station.el;
  if (text) say(station, text);
  wire(station.home, CENTRE, station.color, 14);
  Sound.handoff();
  el.classList.remove('busy');
  clearInterval(station.timer);
  station.since = 0;
  setTimeout(() => { el.classList.remove('awake', 'focus'); dock(); }, 2600);
  if (![...state.stations].some(s => s.el.classList.contains('busy')))
    $('#core').classList.remove('busy');
}

/* ── hud ────────────────────────────────────────────────────────────────── */

function applyProject(project) {
  const stages = state.roster?.stages ?? [];
  const at = stages.indexOf(project?.stage);
  $('#stages').innerHTML = stages
    .map((s, i) => `<div class="${at < 0 ? '' : i < at ? 'done' : i === at ? 'now' : ''}"><b>${s}</b></div>`)
    .join('');

  const ruled = new Map((project?.gates ?? []).map(g => [g.id, g]));
  quests(project);
  $('#gates').innerHTML = (state.roster?.gates ?? [])
    .map(g => {
      const r = ruled.get(g.id);
      const cls = r?.result === 'pass' ? 'pass' : r?.result === 'fail' ? 'fail' : '';
      const attempt = r?.attempt > 1 ? ` · รอบ ${r.attempt}` : '';
      return `<i class="${cls}" title="${g.th}${attempt}">${g.id}</i>`;
    }).join('');
}

function quests(project) {
  const ruled = new Map((project?.gates ?? []).map(g => [g.id, g]));
  $('#qlist').innerHTML = (state.roster?.gates ?? []).map(g => {
    const r = ruled.get(g.id);
    const cls = r?.result === 'pass' ? 'done' : r?.result === 'fail' ? 'fail' : '';
    const mark = r?.result === 'pass' ? '✓' : r?.result === 'fail' ? '✕' : '';
    const tries = r?.attempt > 1 ? `<span class="n">รอบ ${r.attempt}</span>` : '';
    return `<li class="${cls}"><span class="tick">${mark}</span>${g.id} · ${g.th}${tries}</li>`;
  }).join('');
}

/** Shorten a shell command to the part that carries meaning.
 *  A feed line reading `cd /Users/plug/Development/design-lazyyy/skills; grep -rn
 *  "REGISTER.md" --include=*.md --include=*.sh …` wrapped over four lines and
 *  said almost nothing; the verb and its target say the same thing in one. */
function shorten(text) {
  let t = String(text ?? '').replace(/\s+/g, ' ').trim();
  t = t.replace(/^cd\s+\S+\s*(&&|;)\s*/, '');            // drop the cd prefix
  t = t.replace(/\/Users\/[^/]+\/[^\s'"]*\/(skills|projects)\//g, '');  // absolute → relative
  t = t.replace(/\s+2>&1|\s+2>\/dev\/null|\s+\|\s*head\s+-?\d+/g, ''); // shell noise
  return t;
}

function log(html) {
  const div = document.createElement('div');
  div.innerHTML = html;
  div.title = div.textContent;          // full text on hover, one line on screen
  feed.appendChild(div);
  while (feed.children.length > 9) feed.firstChild.remove();
  // newest at the bottom, so the eye has a fixed place to look
  feed.scrollTop = feed.scrollHeight;
}

function verdict(word, note) {
  const box = $('#verdict');
  box.className = word || '';
  $('#vword').textContent = word || 'รอคำตัดสิน';
  $('#vnote').textContent = note || '';
  $('#stage').classList.toggle('blocked', word === 'BLOCKED');
  if (word === 'PASS') Sound.pass();
  if (word === 'CORRECTED') Sound.corrected();
  if (word === 'BLOCKED') Sound.blocked();
}

const label = s => `<b style="color:${s.color}">${s.name}</b>`;

/* ── controller ─────────────────────────────────────────────────────────── */

const control = (action, extra = {}) =>
  fetch('/control', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action, ...extra }),
  }).then(r => r.json()).catch(() => ({}));

/** The bar shows the one project this room is for.
 *  A row of tabs invited a mis-click mid-run — and switching is not a thing you
 *  do while a pipeline is writing files, it is a thing you do by leaving. */
function buildTabs() {
  const tabs = $('#tabs');
  const p = state.projects?.[state.active];
  if (!p) { tabs.innerHTML = '<span class="none">ยังไม่ได้เลือกโปรเจกต์</span>'; return; }
  tabs.innerHTML = `
    <span class="here" data-code="${state.active}"><b>${state.active}</b><u>${escape(p.name ?? '')}</u></span>
    <button id="leave" title="กลับไปหน้าเลือกโปรเจกต์">เปลี่ยน</button>`;
  $('#leave').addEventListener('click', () => {
    if (state.running && !confirm('สายงานกำลังทำงานอยู่ · ออกไปหน้าเลือกโปรเจกต์เลยไหม')) return;
    $('#splash').classList.remove('gone');
    $('#newproj').hidden = true;
    $('#pick').hidden = false;
    buildPicker();
  });
}

/** Mark the tab of whichever project an event belongs to. */
function markBusy(code) {
  if (!code) return;
  const tab = $(`#tabs [data-code="${CSS.escape(code)}"]`);
  if (!tab) return;
  tab.classList.add('busy');
  clearTimeout(tab._t);
  tab._t = setTimeout(() => tab.classList.remove('busy'), 8000);
}

/* ── chat ───────────────────────────────────────────────────────────────── */

/** Open the panel when there is something in it worth reading. A box that sits
 *  open all session saying "no commands yet" is furniture; one that appears when
 *  the crew speaks is a conversation. */
function openChat() {
  const box = $('#chat');
  if (!box.classList.contains('min')) return;
  box.classList.remove('min');
  $('#chat-min').textContent = '–';
  $('#chat-min').setAttribute('aria-expanded', 'true');
}

function chatLine(who, text, isError = false) {
  openChat();
  const log = $('#chat-log');
  const div = document.createElement('div');
  div.className = `msg ${who}${isError ? ' err' : ''}`;
  div.textContent = text;
  log.appendChild(div);
  while (log.children.length > 60) log.firstChild.remove();
  log.scrollTop = log.scrollHeight;
}

function wireChat(canRun) {
  const form = $('#chat-form'), input = $('#chat-in'), send = $('#chat-send');

  if (!canRun) {
    input.disabled = send.disabled = true;
    input.placeholder = 'เปิดเซิร์ฟเวอร์ด้วย --allow-run เพื่อสั่งงานจากหน้านี้';
  }

  const submit = async () => {
    const text = input.value.trim();
    if (!text) return;
    input.value = '';
    send.disabled = true;
    const r = await control('say', { text });
    if (r.error) { chatLine('crew', r.error, true); send.disabled = false; }
  };

  form.addEventListener('submit', e => { e.preventDefault(); submit(); });
  // Enter sends, Shift+Enter breaks the line — a brief is often more than one.
  input.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); submit(); }
  });

  $('#chat-new').addEventListener('click', async () => {
    await control('newchat');
    $('#chat-log').innerHTML = '';
  });

  $('#chat-min').addEventListener('click', () => {
    const box = $('#chat');
    box.classList.toggle('min');
    $('#chat-min').textContent = box.classList.contains('min') ? '+' : '–';
    $('#chat-min').setAttribute('aria-expanded', String(!box.classList.contains('min')));
  });
}

function wireControls(transport, canRun, mode) {
  const play = $('#c-play');
  const paint = t => {
    play.textContent = t?.paused ? '▶' : '⏸';
    play.setAttribute('aria-label', t?.paused ? 'เล่น' : 'หยุดชั่วคราว');
  };
  paint(transport);

  play.addEventListener('click', async () => paint(await control(play.textContent === '▶' ? 'play' : 'pause')));
  $('#c-restart').addEventListener('click', () => control('restart'));
  for (const b of document.querySelectorAll('.speeds button')) {
    b.addEventListener('click', async () => {
      await control('speed', { value: Number(b.dataset.speed) });
      for (const o of document.querySelectorAll('.speeds button')) o.classList.toggle('on', o === b);
    });
  }

  // Rewind and speed belong to a recording. Leaving them on screen during a
  // live run — greyed out but present — read as "you can pause the work", which
  // is the one thing they cannot do. In live mode they are not there at all.
  if (mode !== 'replay') {
    $('#control .transport').hidden = true;
    $('#control .transport').previousElementSibling?.remove();
  }

  const run = $('#c-run');
  $('#c-stop').remove();               // one control, two states
  if (!canRun) {
    run.disabled = true;
    run.title = 'เปิดเซิร์ฟเวอร์ด้วย --allow-run เพื่อสั่งงานจากหน้านี้';
  }
  run.addEventListener('click', async () => {
    if (state.running) {
      if (!confirm('หยุดสายงานที่กำลังทำงานอยู่?')) return;
      const r = await control('stop');
      if (r.error) toast('หยุดไม่ได้', r.error, '#FB7185');
      return;
    }
    const r = await control('run');
    if (r.error) { toast('สั่งไม่ได้', r.error, '#FB7185'); return; }
    log('<b style="color:#34D399">สั่งสายงานทำงานแล้ว</b>');
  });
}

/* ── the stream ─────────────────────────────────────────────────────────── */

/* The stream has to survive the server restarting under it — which happens
   every time the monitor itself is edited, and happened while a run was live.
   The old code wrote "disconnected" into a label and stopped there, so the room
   sat frozen next to a pipeline that was still working. */
let source;
let retry = 0;

function connect() {
  source = new EventSource('/events');

  source.onopen = () => {
    retry = 0;
    $('#mode').textContent = state.mode === 'replay' ? 'เล่นซ้ำ' : 'สด';
    $('#mode').className = 'chip ' + (state.mode ?? 'live');
  };

  source.onerror = () => {
    if (source.readyState === EventSource.CLOSED) {
      // EventSource gives up on some failures; reopen it ourselves, backing off
      // so a server that is down does not get hammered.
      retry = Math.min(retry + 1, 6);
      $('#mode').textContent = `ต่อใหม่ใน ${retry * 2}s`;
      $('#mode').className = 'chip';
      setTimeout(connect, retry * 2000);
    } else {
      $('#mode').textContent = 'กำลังต่อใหม่…';
      $('#mode').className = 'chip';
    }
  };

  wireStream();
}

function wireStream() {
  source.addEventListener('project', e => applyProject(JSON.parse(e.data)));

  source.addEventListener('projects', e => {
  state.projects = JSON.parse(e.data);
  applyProject(state.projects[state.active] ?? { stage: null, gates: [] });
  buildTabs();
});

  source.addEventListener('active', e => {
  state.active = JSON.parse(e.data).code;
  buildTabs();
});

  source.addEventListener('transport', e => {
  const t = JSON.parse(e.data);
  const play = $('#c-play');
  play.textContent = t.paused ? '▶' : '⏸';
});

  source.addEventListener('chat', e => {
  const { who, text } = JSON.parse(e.data);
  chatLine(who, text);
});

    source.addEventListener('hook', e => {
    const ev = JSON.parse(e.data);

    // A run announced by the script itself — the button must reflect it whether
    // the run came from the button or from a terminal.
    if (ev.kind === 'run') {
      const run = $('#c-run');
      state.running = ev.state === 'started';
      brand();
      if (state.running) {
        run.classList.add('running');
        run.textContent = '■ หยุดสายงาน';
      } else {
        run.classList.remove('running');
        run.textContent = '▶ สั่งสายงานทำงาน';
      }
      return;
    }

    if (ev.kind !== 'stage') return;

    // Wake the desk whose role this stage belongs to. Without this the room
    // stayed dark for the whole run, because a role driven from the shell never
    // produces the SubagentStart the characters listen for.
    const st = ev.agent ? resolve(ev.agent, null) : null;
    if (st) {
      if (ev.state === 'done') {
        finish(st, `${ev.stage} เสร็จ`);
      } else {
        dispatch(st);
        paint(st, `กำลังทำระยะ ${ev.stage}`);
      }
    }

    const box = $('#progress');
    box.hidden = false;
    // done = stages finished before this one; the current stage counts as
    // started, not finished, which is why the bar sits behind the label
    const done = Math.max(0, ev.index - 1);
    const pct = Math.round((done / ev.total) * 100);
    box.querySelector('.bar i').style.width = pct + '%';
    box.querySelector('.pct').textContent = pct + '%';
    box.querySelector('.what').textContent = `${ev.stage} · ระยะ ${ev.index}/${ev.total}`;
  });

  source.addEventListener('run', e => {
    const { state: st, code } = JSON.parse(e.data);
    const run = $('#c-run');
    $('#chat-send').disabled = st === 'started';
    state.running = st === 'started';
    brand();
    if (st === 'started') {
      openChat();
      run.classList.add('running');
      run.textContent = '■ หยุดสายงาน';
      run.title = 'สายงานกำลังทำงาน · กดเพื่อหยุด';
      toast('เริ่มแล้ว', 'สายงานกำลังทำงานจริง', '#34D399');
    } else {
      run.classList.remove('running');
      run.textContent = '▶ สั่งสายงานทำงาน';
      run.title = '';
      if (st === 'ended' && code === 0) {
        const box = $('#progress');
        box.querySelector('.bar i').style.width = '100%';
        box.querySelector('.pct').textContent = '100%';
        box.querySelector('.what').textContent = 'ครบทุกระยะ';
      }
      toast(st === 'stopped' ? 'หยุดแล้ว' : 'จบแล้ว',
            st === 'stopped' ? 'ผู้ใช้สั่งหยุด' : `จบด้วยรหัส ${code ?? '—'}`,
            st === 'stopped' ? '#F0B429' : '#7DD3FC');
    }
  });

  source.addEventListener('reset', () => {
  feed.innerHTML = '';
  Object.assign(game, { xp: 0, acts: 0, handoffs: 0, streak: 0, best: 0 });
  game.unlocked.clear();
  scoreboard();
  for (const s of state.stations) {
    s.xp = 0;
    s.el.querySelector('.xp i').style.width = '0%';
  }
  verdict(null, '');
  for (const s of state.stations) {
    s.el.classList.remove('awake', 'busy', 'walking', 'rework');
    s.el.style.left = s.home.x + '%';
    s.el.style.top = s.home.y + '%';
    clearInterval(s.timer);
  }
});

  source.addEventListener('hook', e => {
  const ev = JSON.parse(e.data);
  markBusy(ev.project);
  if (ev.session && ev.session !== watchedSession) { watchedSession = ev.session; pollUsage(); }
  const station = ev.agent ? resolve(ev.agent, ev.path) : null;

  switch (ev.kind) {
    case 'prompt':
      Sound.order();
      log(`<b>เจ้าของโปรเจกต์</b> สั่ง — ${escape(shorten(ev.text).slice(0, 90))}`);
      $('#brief').innerHTML = `<b>คำสั่งภารกิจ</b>${escape(ev.text ?? '')}`;
      $('#brief').classList.add('on');
      $('#core').classList.add('busy');
      break;

    case 'agent_start':
      if (!station) { log(`<b>${escape(ev.agent)}</b> เริ่มทำงาน (ยังไม่มีโต๊ะของตัวเอง)`); break; }
      log(`${label(station)} ได้รับคำสั่ง`);
      dispatch(station);
      break;

    case 'tool': {
      const target = station ?? resolve(ev.agent, ev.path);
      if (ev.verdict) {
        const note = { PASS: 'ตรวจแล้ว ผ่าน', CORRECTED: 'ยังไม่ผ่าน ต้องแก้แล้วตรวจใหม่',
                       BLOCKED: 'หยุดไว้ก่อน ต้องให้คนจริงมาทำ' }[ev.verdict];
        verdict(ev.verdict, note);
        log(`<b style="color:#7DD3FC">correcter</b> — ${ev.verdict}`);
        if (ev.verdict === 'PASS') {
          game.streak++;
          game.best = Math.max(game.best, game.streak);
          game.xp += 200;
          toast('ประตูผ่าน', `correcter รับรอง · ผ่านติดกัน ${game.streak}`, '#34D399');
          Sound.gate();
          if (game.streak === 3) once('s3', 'ปลดล็อก', 'ผ่านสามประตูรวด', '#34D399');
        } else {
          if (game.streak >= 3) once('broke', 'สถิติจบ', `ผ่านติดกันสูงสุด ${game.best}`, '#F0B429');
          game.streak = 0;
          if (ev.verdict === 'CORRECTED') toast('ตีกลับ', 'ตีกลับให้แก้ แล้วตรวจใหม่', '#F0B429');
          if (ev.verdict === 'BLOCKED') toast('หยุดสายงาน', 'เขียนโค้ดเพิ่มไม่ช่วย ต้องให้คนจริงมาทำ', '#FB7185');
        }
        scoreboard();
        if (ev.verdict === 'CORRECTED') {
          const back = state.stations.find(s => s.el.classList.contains('busy'));
          if (back) {
            back.el.classList.add('rework');
            wire(CENTRE, back.home, '#F0B429', 20);
            setTimeout(() => back.el.classList.remove('rework'), 1200);
          }
        }
        break;
      }
      if (!target) {
        // No agent on the event means the orchestrator itself did it. Dropping
        // these made the room look asleep while the lead was reading the repo,
        // planning, and running the correcter — which is most of a run.
        game.acts++;
        const doing = ev.path ? `${ev.tool} ${ev.path}` : `${ev.tool} ${shorten(ev.text)}`.trim();
        $('#core-doing').textContent = doing;
        $('#core').classList.add('busy');
        log(`<b style="color:#7DD3FC">ORCHESTRATOR</b> ${escape(doing)}`);
        scoreboard();
        Sound.tick();
        break;
      }
      target.acts++;
      game.acts++;
      const what = ev.path ? `${ev.tool} ${ev.path}` : `${ev.tool} ${shorten(ev.text)}`.trim();
      paint(target, what);
      award(target, 10);
      if (ev.path) log(`${label(target)} ${escape(what)}`);
      if (game.acts === 1) once('first', 'ปลดล็อก', 'ลงมือครั้งแรกของสายงาน');
      Sound.tick();
      break;
    }

    case 'agent_stop': {
      if (!station) break;
      game.handoffs++;
      log(`${label(station)} ส่งงาน`);
      award(station, 50, 'ส่งงานสำเร็จ');
      finish(station, ev.text || 'เสร็จแล้ว');
      dock();
      if (game.handoffs === 1) once('h1', 'ปลดล็อก', 'ส่งไม้ต่อครั้งแรก', '#34D399');
      break;
    }

    case 'turn_end':
      $('#core').classList.remove('busy');
      $('#core-doing').textContent = '';
      break;

    case 'standing':
      log(`<b style="color:#F0B429">ยังเปิดอยู่</b> ${escape(ev.text ?? '')}`);
      $('#vnote').textContent = ev.text ?? '';
      toast('สายงานจบรอบ', 'ผ่านครบทุกด่าน', '#34D399');
      break;

    case 'session_start':
      log('<b>เปิดห้อง</b> — session เริ่มแล้ว');
      break;
  }
});
}

connect();

function escape(s) {
  return String(s).replace(/[<>&]/g, c => ({ '<': '&lt;', '>': '&gt;', '&': '&amp;' }[c]));
}

/* ── entrance ───────────────────────────────────────────────────────────── */

/** Choosing a project is the first thing that happens, so it happens first —
 *  before the room, not buried in a chat box behind it. */
function buildPicker() {
  const list = $('#pick-list');
  const gates = state.roster?.gates ?? [];
  list.innerHTML = Object.entries(state.projects).map(([code, p]) => {
    const ruled = new Map((p.gates ?? []).map(g => [g.id, g]));
    const dots = gates.map(g => {
      const r = ruled.get(g.id);
      return `<i class="${r?.result === 'pass' ? 'pass' : r?.result === 'fail' ? 'fail' : ''}"></i>`;
    }).join('');
    return `<button class="proj" data-code="${code}">
        <b>${code}</b>
        <span class="who"><span>${escape(p.name ?? code)}</span><em>ระยะ ${p.stage ?? 'ยังไม่เริ่ม'}</em></span>
        <span class="gates">${dots}</span>
      </button>`;
  }).join('');

  for (const b of list.querySelectorAll('.proj')) {
    b.addEventListener('click', () => enterRoom(b.dataset.code));
  }
}

async function enterRoom(code) {
  if (code && code !== state.active) {
    const r = await control('switch', { code });
    if (r.active) state.active = r.active;
  }
  applyProject(state.projects[state.active] ?? { stage: null, gates: [] });
  buildTabs();
  brand();
  $('#splash').classList.add('gone');
}

/* ── workspace chooser ──────────────────────────────────────────────────── */

/** The native chooser, opened by the server. Asking the browser for a folder
 *  gives a handle with no path behind it; a symlink and a shell script both
 *  need the path, so the dialog is opened on the machine instead. */
$('#ws-pick').addEventListener('click', async () => {
  const btn = $('#ws-pick');
  btn.disabled = true; btn.textContent = 'กำลังเลือก…';
  const picked = await control('pickdir');
  btn.disabled = false; btn.textContent = 'เลือกโฟลเดอร์…';

  if (picked.cancelled) return;
  if (picked.error) { toast('เลือกไม่ได้', picked.error, '#FB7185'); return; }

  const r = await control('workspace', { path: picked.path });
  if (r.error) { toast('ใช้โฟลเดอร์นี้ไม่ได้', r.error, '#FB7185'); return; }

  state.workspace = r.workspace;
  $('#ws-path').textContent = r.workspace;
  const fresh = await fetch('/state').then(x => x.json());
  state.projects = fresh.projects;
  state.active = fresh.active;
  buildPicker();
  buildTabs();
});

$('#pick-new').addEventListener('click', () => {
  $('#pick').hidden = true;
  $('#browse').hidden = true;
  $('#newproj').hidden = false;
  $('#newproj [name=name]').focus();
});
$('#np-cancel').addEventListener('click', () => {
  $('#newproj').hidden = true;
  $('#pick').hidden = false;
});

// suggest a code from the name, but let it be overtyped
$('#newproj [name=name]').addEventListener('input', e => {
  const codeField = $('#newproj [name=code]');
  if (codeField.dataset.touched) return;
  const words = e.target.value.trim().split(/\s+/).filter(Boolean);
  codeField.value = (words.length > 1
    ? words.map(w => w[0]).join('')
    : (e.target.value.replace(/[^A-Za-z0-9ก-๙]/g, ''))
  ).toUpperCase().replace(/[^A-Z0-9]/g, '').slice(0, 3);
});
$('#newproj [name=code]').addEventListener('input', e => { e.target.dataset.touched = '1'; });

$('#newproj [name=git]').addEventListener('change', e => {
  $('#remote-wrap').hidden = e.target.value !== 'remote';
});

$('#newproj').addEventListener('submit', async e => {
  e.preventDefault();
  const err = $('#np-err');
  err.hidden = true;
  const data = Object.fromEntries(new FormData(e.target).entries());
  data.code = String(data.code || '').toUpperCase();
  const go = $('#np-go');
  go.disabled = true; go.textContent = 'กำลังเปิด…';

  const r = await control('create', { action: 'create', ...data });
  go.disabled = false; go.textContent = 'เปิดโครงการ';

  if (r.error) { err.textContent = r.error; err.hidden = false; return; }

  const fresh = await fetch('/state').then(x => x.json());
  state.projects = fresh.projects;
  state.active = fresh.active;
  buildPicker();
  await enterRoom(r.code);
  log(`<b style="color:#34D399">เปิดโปรเจกต์ ${escape(r.code)}</b> — ${escape(data.name)}`);
  if (r.open) toast('มีคำถามค้าง', `${r.open} ข้อยังเป็น TBD`, '#F0B429');
  if (r.git === 'init')   toast('git', 'สร้าง repo และคอมมิตแรกแล้ว', '#7DD3FC');
  if (r.git === 'remote') toast('git', 'เชื่อม origin แล้ว · ยังไม่ push', '#7DD3FC');
  if (typeof r.git === 'string' && r.git.startsWith('failed')) toast('git ล้มเหลว', r.git, '#FB7185');
  chatLine('crew', `เปิดโปรเจกต์ ${r.code} แล้ว · พิมพ์ /gate เพื่อดูว่ายังขาดอะไร`);
});
$('#audio').addEventListener('click', () => {
  Sound.arm();
  $('#audio').setAttribute('aria-pressed', String(Sound.toggle()));
});
