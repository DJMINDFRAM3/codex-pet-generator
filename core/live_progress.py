"""
Live progress — one Slack message that updates itself while the monitor works.

State lives on disk because three separate processes need it: the monitor, the
hook (a fresh process per tool call), and the progress thread.

The steps stay in their own file, apart from the message id. The hook appends to
it on every tool call and a turn can hold several, so sharing one file would let
a late write wipe the id — exactly what broke the length hook's hand-off flag.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from constants import (
    LIVE_PROGRESS_LABEL_CHARS,
    LIVE_PROGRESS_MAX_STEPS,
    LIVE_PROGRESS_STATE_PATH,
    LIVE_PROGRESS_STEPS_PATH,
    MONITOR_MINUTES_THRESHOLD,
)

BAR_WIDTH = 10
BAR_FILLED = "▓"
BAR_EMPTY = "░"
DONE_MARK = "✅"
PENDING_MARK = "⏳"

OPENING_TEXT = "🥷 On it — working on this now…"

_FILE_TOOLS = ("Read", "Write", "Edit", "NotebookEdit")


def read_state() -> dict:
    """Return the active run's state, or {} when live progress is not running."""
    try:
        with open(LIVE_PROGRESS_STATE_PATH) as handle:
            state = json.load(handle)
    except (OSError, ValueError):
        return {}
    return state if isinstance(state, dict) else {}


def arm(*, channel: Optional[str], thread_ts: Optional[str]) -> None:
    """Mark a run as started. Nothing is posted yet, so ``ts`` stays empty."""
    payload = {
        "channel": channel,
        "ts": "",
        "thread_ts": thread_ts,
        "started_at": datetime.now(timezone.utc).timestamp(),
    }
    with open(LIVE_PROGRESS_STATE_PATH, "w") as handle:
        json.dump(payload, handle)
    # Drop the last run's steps so they don't show up under the new message.
    Path(LIVE_PROGRESS_STEPS_PATH).unlink(missing_ok=True)


def mark_posted(*, channel: str, ts: str) -> bool:
    """Record the message to keep editing.

    False means the run ended mid-post, so nobody owns that message — the
    caller has to delete it or it sits in the channel forever.
    """
    state = read_state()
    if not state:
        return False
    state["channel"] = channel or state.get("channel")
    state["ts"] = ts
    with open(LIVE_PROGRESS_STATE_PATH, "w") as handle:
        json.dump(state, handle)
    return True


def seconds_running(state: dict, *, now: Optional[float] = None) -> float:
    """How long the current run has been going. 0.0 if the state is unusable."""
    now = datetime.now(timezone.utc).timestamp() if now is None else now
    try:
        return max(0.0, now - float(state.get("started_at")))
    except (TypeError, ValueError):
        return 0.0


def clear_state() -> None:
    """Forget the message. Safe to call when nothing is running."""
    Path(LIVE_PROGRESS_STATE_PATH).unlink(missing_ok=True)
    Path(LIVE_PROGRESS_STEPS_PATH).unlink(missing_ok=True)


def label_for(payload: Dict[str, Any]) -> str:
    """Pick something worth showing the user for this tool call.

    Bash gives us the model's own one-line description, file tools give a path.
    """
    tool = str(payload.get("tool_name") or "").strip() or "step"
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        return tool

    if tool == "Bash":
        described = str(tool_input.get("description") or "").strip()
        return described or tool
    if tool in _FILE_TOOLS:
        path = str(tool_input.get("file_path") or "").strip()
        return f"{tool} {os.path.basename(path)}" if path else tool
    if tool == "Skill":
        skill = str(tool_input.get("skill") or "").strip()
        return f"Skill {skill}" if skill else tool
    return tool


def record_step(payload: Dict[str, Any]) -> bool:
    """Add this tool call to the checklist. False when no run is active.

    Runs on every tool call, so it stays cheap: one small read, one append, no
    network. Appending also means two hooks at once can't lose each other's line.
    """
    if not read_state():
        return False

    entry = {
        "t": datetime.now(timezone.utc).timestamp(),
        "label": label_for(payload)[:LIVE_PROGRESS_LABEL_CHARS],
    }
    try:
        with open(LIVE_PROGRESS_STEPS_PATH, "a") as handle:
            handle.write(json.dumps(entry) + "\n")
    except OSError:
        return False
    return True


def read_steps() -> List[dict]:
    """Every step recorded for the current run, oldest first."""
    steps: List[dict] = []
    try:
        with open(LIVE_PROGRESS_STEPS_PATH) as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except ValueError:
                    continue
                if isinstance(entry, dict) and entry.get("label"):
                    steps.append(entry)
    except OSError:
        return []
    return steps


def _bar(fraction: float) -> str:
    filled = max(0, min(BAR_WIDTH, round(fraction * BAR_WIDTH)))
    return BAR_FILLED * filled + BAR_EMPTY * (BAR_WIDTH - filled)


def _elapsed_text(seconds: float) -> str:
    if seconds < 60:
        return f"{int(seconds)}s"
    return f"{int(seconds // 60)}m"


def render(state: dict, steps: List[dict], *, now: Optional[float] = None) -> tuple:
    """Build (blocks, fallback_text) for the progress message.

    Blocks are just for layout. Slack shows "(edited)" after the first update
    either way — the docs say blocks avoid it, but they don't (tested).
    """
    elapsed = seconds_running(state, now=now)
    budget = max(1.0, MONITOR_MINUTES_THRESHOLD * 60)

    # No blank lines, only the newest few steps: Slack's thread pane folds
    # anything past about five lines behind a "Show more".
    lines = ["🥷 *Working on it…*"]
    lines.extend(f"{DONE_MARK} {s['label']}" for s in steps[-LIVE_PROGRESS_MAX_STEPS:])
    if not steps:
        lines.append(f"{PENDING_MARK} Getting started")

    counted = f"{len(steps)} step{'s' if len(steps) != 1 else ''}"
    lines.append(
        f"`{_bar(elapsed / budget)}`  {counted} · {_elapsed_text(elapsed)} elapsed"
    )

    body = "\n".join(lines)
    blocks = [{"type": "section", "text": {"type": "mrkdwn", "text": body}}]
    fallback = f"🥷 Working on it… {counted} · {_elapsed_text(elapsed)} elapsed"
    return blocks, fallback
