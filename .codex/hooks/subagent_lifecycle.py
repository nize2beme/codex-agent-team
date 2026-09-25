#!/usr/bin/env python3
"""Fail-open subagent lifecycle logger with cross-platform write locking."""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone


def codex_home() -> str:
    configured = os.environ.get("CODEX_HOME")
    if configured:
        return os.path.abspath(os.path.expanduser(configured))
    home = os.environ.get("HOME") or os.environ.get("USERPROFILE") or os.path.expanduser("~")
    return os.path.join(os.path.abspath(os.path.expanduser(home)), ".codex")


LOG_DIR = os.path.join(codex_home(), "team-logs")
LOG_PATH = os.path.join(LOG_DIR, "subagent-events.jsonl")
LOCK_PATH = f"{LOG_PATH}.lock"
MAX_LOG_BYTES = 1_048_576
BACKUP_COUNT = 3
ALLOWED_PAYLOAD_KEYS = {
    "agent_id",
    "agent_type",
    "cwd",
    "hook_event_name",
    "permission_mode",
    "session_id",
    "state",
    "stop_hook_active",
    "turn_id",
}


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def rotate_log(path: str) -> None:
    try:
        if not os.path.exists(path) or os.path.getsize(path) < MAX_LOG_BYTES:
            return
        oldest_backup = f"{path}.{BACKUP_COUNT}"
        if os.path.exists(oldest_backup):
            os.remove(oldest_backup)
        for index in range(BACKUP_COUNT - 1, 0, -1):
            source = f"{path}.{index}"
            target = f"{path}.{index + 1}"
            if os.path.exists(source):
                os.replace(source, target)
        os.replace(path, f"{path}.1")
    except Exception:
        pass


def filtered_payload(payload: object) -> dict:
    if not isinstance(payload, dict):
        return {}
    return {
        key: value
        for key, value in payload.items()
        if key in ALLOWED_PAYLOAD_KEYS
    }


def lock_file(handle) -> None:
    if os.name == "nt":
        import msvcrt

        handle.seek(0, os.SEEK_END)
        if handle.tell() == 0:
            handle.write(b"\0")
            handle.flush()
        handle.seek(0)
        msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
        return

    import fcntl

    fcntl.flock(handle.fileno(), fcntl.LOCK_EX)


def unlock_file(handle) -> None:
    if os.name == "nt":
        import msvcrt

        handle.seek(0)
        msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        return

    import fcntl

    fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def main() -> int:
    state = sys.argv[1] if len(sys.argv) > 1 else "unknown"
    try:
        raw = sys.stdin.read().strip()
        payload = json.loads(raw) if raw else {}
    except Exception:
        payload = {}

    record = {
        "captured_at": now(),
        "event": "SubagentLifecycle",
        "state": state,
        "payload": filtered_payload(payload),
    }
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
        with open(LOCK_PATH, "a+b") as lock_handle:
            lock_file(lock_handle)
            try:
                rotate_log(LOG_PATH)
                with open(LOG_PATH, "a", encoding="utf-8") as handle:
                    handle.write(json.dumps(record) + "\n")
            finally:
                unlock_file(lock_handle)
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
