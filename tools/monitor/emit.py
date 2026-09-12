#!/usr/bin/env python3
"""emit — the hook receiver behind the mission-control monitor.

Reads one Claude Code hook payload on stdin and appends one normalised record
to `.monitor/events.jsonl`, which `server.mjs` tails and streams to the room.

The contract with the running session, in order of importance:

  1. **Never exit non-zero.** A non-zero exit prints a hook error into the
     student's transcript. Losing one frame of an animation is cheap; making
     every tool call in the lesson look broken is not.
  2. **Never raise.** Every failure path ends in a silent return.
  3. **Stay cheap.** The hook is configured `async: true`, but a hook that
     takes a second still costs a second of someone's attention.

Self-test — proves 1 and 2 rather than asserting them:

    python3 emit.py --selftest
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path

# Keep every line comfortably under PIPE_BUF (4096 bytes) so that a single
# append from a subagent cannot interleave with one from the main agent.
# Two agents writing at once is the normal case here, not the rare one.
TEXT_LIMIT = 400

VERDICT_RE = re.compile(r"คำตัดสิน:\s*(PASS|CORRECTED|BLOCKED)")
PROJECT_RE = re.compile(r"^projects/([A-Z0-9_-]{2,12})/")


def repo_root() -> Path:
    """Where `.monitor/` lives.

    `CLAUDE_PROJECT_DIR` is set for hook commands and is the honest answer.
    The fallback walks up from this file (tools/monitor/emit.py -> repo) so
    the self-test works when run by hand with no session around it.
    """
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env:
        p = Path(env)
        if p.is_dir():
            # resolve() matters on macOS, where /tmp and /var are symlinks into
            # /private — without it every path falls back to its basename and
            # the src/ vs server/ split that picks a desk quietly stops working.
            return p.resolve()
    return Path(__file__).resolve().parent.parent.parent


def clip(value: object, limit: int = TEXT_LIMIT) -> str:
    """One line, bounded. Bubbles show a phrase, never a transcript."""
    if not isinstance(value, str):
        return ""
    text = " ".join(value.split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def relative(path: object, root: Path) -> str:
    """Display paths relative to the repo — `project/1-product/PRD.md`."""
    if not isinstance(path, str) or not path:
        return ""
    try:
        return str(Path(path).resolve().relative_to(root))
    except (ValueError, OSError):
        return path.rsplit("/", 1)[-1]


def response_text(response: object) -> str:
    """Tool responses arrive in several shapes depending on the tool."""
    if isinstance(response, str):
        return response
    if isinstance(response, dict):
        for key in ("text", "stdout", "output", "content"):
            value = response.get(key)
            if isinstance(value, str) and value:
                return value
    return ""


def which_project(path: str, root: Path) -> str | None:
    """Which project an event belongs to.

    Read off the path the tool actually touched — `projects/WKO/...` — so two
    sessions working on two projects at the same time stay separated without
    either of them having to announce anything. Only when a path says nothing
    does it fall back to whichever project `project/` currently points at.
    """
    if path:
        found = PROJECT_RE.match(path)
        if found:
            return found.group(1)
    try:
        link = (root / "project")
        if link.is_symlink():
            return Path(os.readlink(link)).name
        marker = root / "projects" / ".active"
        if marker.is_file():
            return marker.read_text(encoding="utf-8").strip() or None
    except OSError:
        pass
    return None


def normalise(payload: dict, root: Path) -> dict | None:
    """Hook payload -> one monitor record, or None when nothing is worth showing.

    `agent_type` rides along on every hook fired from inside a subagent, which
    is what lets a file write be attributed to the character that made it
    rather than to whoever happens to be on screen.
    """
    event = payload.get("hook_event_name")
    if not isinstance(event, str):
        return None

    record: dict[str, object] = {
        "ts": round(time.time(), 3),
        "session": clip(payload.get("session_id"), 64),
    }
    project = which_project("", root)
    if project:
        record["project"] = project
    agent = payload.get("agent_type")
    if isinstance(agent, str) and agent:
        record["agent"] = agent
    agent_id = payload.get("agent_id")
    if isinstance(agent_id, str) and agent_id:
        record["agent_id"] = agent_id

    if event == "SessionStart":
        record["kind"] = "session_start"

    elif event == "SessionEnd":
        record["kind"] = "session_end"

    elif event == "UserPromptSubmit":
        record["kind"] = "prompt"
        record["text"] = clip(payload.get("prompt"))

    elif event == "SubagentStart":
        record["kind"] = "agent_start"

    elif event == "SubagentStop":
        record["kind"] = "agent_stop"
        record["text"] = clip(payload.get("last_assistant_message"))

    elif event == "Stop":
        record["kind"] = "turn_end"

    elif event in ("PostToolUse", "PostToolUseFailure"):
        tool = payload.get("tool_name")
        if not isinstance(tool, str):
            return None
        tool_input = payload.get("tool_input")
        tool_input = tool_input if isinstance(tool_input, dict) else {}

        record["kind"] = "tool"
        record["tool"] = tool
        record["ok"] = event == "PostToolUse"

        path = relative(tool_input.get("file_path"), root)
        if path:
            record["path"] = path
            project = which_project(path, root)
            if project:
                record["project"] = project

        if tool == "Bash":
            command = clip(tool_input.get("command"), 200)
            record["text"] = command
            # The correcter is the only thing in this repo allowed to say
            # whether the work stands, so its verdict gets its own field.
            if "verify.py" in command:
                found = VERDICT_RE.search(response_text(payload.get("tool_response")))
                if found:
                    record["verdict"] = found.group(1)
    else:
        return None

    return record


def append(record: dict, root: Path) -> None:
    directory = root / ".monitor"
    directory.mkdir(parents=True, exist_ok=True)
    line = json.dumps(record, ensure_ascii=False) + "\n"
    # O_APPEND + one write() is atomic below PIPE_BUF; `clip` keeps it there.
    with open(directory / "events.jsonl", "a", encoding="utf-8") as handle:
        handle.write(line)


def handle(raw: str) -> None:
    try:
        payload = json.loads(raw)
        if not isinstance(payload, dict):
            return
        root = repo_root()
        record = normalise(payload, root)
        if record is not None:
            append(record, root)
    except Exception:
        # Rule 2. There is no failure here worth interrupting a lesson for.
        return


def selftest() -> int:
    """Feed the shapes a real session produces, plus the ones it never should."""
    import tempfile

    failures: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        os.environ["CLAUDE_PROJECT_DIR"] = tmp
        root = Path(tmp)
        log = root / ".monitor" / "events.jsonl"

        good = [
            {"hook_event_name": "SessionStart", "session_id": "s1"},
            {"hook_event_name": "UserPromptSubmit", "session_id": "s1",
             "prompt": "ทำให้จบเลย"},
            {"hook_event_name": "SubagentStart", "session_id": "s1",
             "agent_type": "product-owner", "agent_id": "sub-1"},
            {"hook_event_name": "PostToolUse", "session_id": "s1",
             "agent_type": "product-owner", "tool_name": "Write",
             "tool_input": {"file_path": f"{tmp}/projects/WKO/1-product/PRD-WKO-001.md"}},
            {"hook_event_name": "SubagentStop", "session_id": "s1",
             "agent_type": "product-owner", "agent_id": "sub-1",
             "last_assistant_message": "เขียน PRD ฉบับ 01 เสร็จแล้ว"},
            {"hook_event_name": "PostToolUse", "session_id": "s1",
             "tool_name": "Bash",
             "tool_input": {"command": "python3 tools/correcter/verify.py"},
             "tool_response": {"text": "════\nคำตัดสิน: BLOCKED\n  สายงานเดินต่อไม่ได้"}},
        ]
        for payload in good:
            handle(json.dumps(payload))

        lines = log.read_text(encoding="utf-8").splitlines() if log.exists() else []
        if len(lines) != len(good):
            failures.append(f"เขียนได้ {len(lines)} บรรทัด ควรได้ {len(good)}")

        records = [json.loads(line) for line in lines]
        if records and records[3].get("path") != "projects/WKO/1-product/PRD-WKO-001.md":
            failures.append(f"path ไม่ถูกย่อ: {records[3].get('path')!r}")
        if records and records[3].get("agent") != "product-owner":
            failures.append("ไม่ได้ผูก Write เข้ากับ agent ที่เขียน")
        if records and records[3].get("project") != "WKO":
            failures.append(f"ไม่ได้ติดป้ายโปรเจกต์: {records[3].get('project')!r}")
        if records and records[5].get("verdict") != "BLOCKED":
            failures.append(f"อ่านคำตัดสินไม่ได้: {records[5].get('verdict')!r}")
        if any(len(line.encode()) >= 4096 for line in lines):
            failures.append("มีบรรทัดยาวเกิน PIPE_BUF · การเขียนพร้อมกันจะปนกัน")

        before = len(lines)
        # Rule 1 and 2: none of these may write, raise, or be noticed.
        for junk in ["", "not json", "[]", "null", "{}", '{"hook_event_name": 7}',
                     '{"hook_event_name": "PostToolUse"}',
                     '{"hook_event_name": "SubagentStart", "agent_type": null}']:
            handle(junk)
        after = len(log.read_text(encoding="utf-8").splitlines()) if log.exists() else 0
        if after != before + 1:  # only the SubagentStart with a null agent is real
            failures.append(f"ขยะทำให้เกิด {after - before} บรรทัด ควรได้ 1")

    for line in failures:
        print(f"  ✗ {line}")
    print("selftest: " + ("ผ่าน" if not failures else f"ไม่ผ่าน {len(failures)} ข้อ"))
    return 1 if failures else 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    try:
        handle(sys.stdin.read())
    except Exception:
        pass
    sys.exit(0)
