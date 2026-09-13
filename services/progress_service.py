"""
services.progress_service — keeps the live progress message up to date.

Started once at monitor boot; idle until a run arms the state file.

This can't live in the hook. The hook only fires after a tool call returns, so a
two-minute browser step would freeze the message just when the user wants to see
it moving. It also runs inside the agent's tool loop, where a slow Slack call
would hold the agent up. The hook records steps, this thread does the talking.
"""

from __future__ import annotations

import threading
from typing import Optional

from constants import (
    LIVE_PROGRESS_DELAY_SECONDS,
    LIVE_PROGRESS_INTERVAL_SECONDS,
    MONITOR_SERVICE_NAME,
)
from core import live_progress
from core.logging import get_logger

logger = get_logger(MONITOR_SERVICE_NAME)

# Back off after an error so a bad token or network can't hot-loop.
ERROR_BACKOFF_SECONDS = 30.0

# Stop updating after this many failures in a row. State is kept so the
# end-of-run cleanup can still delete the message.
MAX_UPDATE_FAILURES = 3


class ProgressService:
    """Background thread that edits the live progress message on a timer."""

    def __init__(self, iface, interval_seconds: Optional[float] = None):
        self.iface = iface
        self.interval = float(interval_seconds or LIVE_PROGRESS_INTERVAL_SECONDS)
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._last_rendered: Optional[str] = None
        self._failures = 0

    def start(self) -> bool:
        """Start the daemon thread."""
        self._thread = threading.Thread(
            target=self._run, name="live-progress", daemon=True
        )
        self._thread.start()
        logger.info(f"ProgressService started (interval={self.interval}s)")
        return True

    def stop(self) -> None:
        """Signal the loop to exit (mainly for tests)."""
        self._stop_event.set()

    def _run(self) -> None:
        while not self._stop_event.is_set():
            try:
                self.tick()
                self._stop_event.wait(self.interval)
            except Exception as e:  # never let the thread die
                logger.warning(f"ProgressService tick failed: {e}")
                self._stop_event.wait(ERROR_BACKOFF_SECONDS)

    def tick(self) -> bool:
        """One refresh. Returns True when the message was posted or updated."""
        state = live_progress.read_state()
        if not state:
            self._last_rendered = None
            self._failures = 0
            return False

        if self._failures >= MAX_UPDATE_FAILURES:
            return False

        if not state.get("ts"):
            state = self._post_if_slow_enough(state)
            if not state:
                return False

        steps = live_progress.read_steps()
        blocks, fallback = live_progress.render(state, steps)

        # Comparing the rendered text, not the step count, keeps the timer and
        # bar moving during a long tool call.
        fingerprint = f"{state.get('ts')}|{blocks[0]['text']['text']}"
        if fingerprint == self._last_rendered:
            return False

        updated = self.iface.update_message(
            state["ts"], fallback, blocks=blocks, channel=state.get("channel")
        )
        if updated:
            self._last_rendered = fingerprint
            self._failures = 0
        else:
            self._failures += 1
            if self._failures >= MAX_UPDATE_FAILURES:
                logger.warning("Live progress updates keep failing — stopping")
        return bool(updated)

    def _post_if_slow_enough(self, state: dict):
        """Post the message once the run is slow enough to deserve one.

        None while it is still young. Posting here rather than at dispatch is
        what keeps quick answers from ever showing a checklist.
        """
        if live_progress.seconds_running(state) < LIVE_PROGRESS_DELAY_SECONDS:
            return None

        posted = self.iface.say(
            live_progress.OPENING_TEXT, thread_ts=state.get("thread_ts")
        )
        ts = (posted or {}).get("ts")
        if not ts:
            logger.warning("Live progress message could not be posted")
            return None

        channel = (posted or {}).get("channel") or state.get("channel")
        if not live_progress.mark_posted(channel=channel, ts=ts):
            # Run finished mid-post, so nobody owns this message. Take it back.
            self.iface.delete_message(ts, channel=channel)
            return None
        logger.info(f"Live progress posted (ts={ts})")
        # Hand it back so this same tick draws the checklist right away.
        state["ts"], state["channel"] = ts, channel
        return state
