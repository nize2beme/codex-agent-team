#!/usr/bin/env python3
"""Tests for session-start log filtering and Codex home selection."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).with_name("session_start.py")


class SessionStartTest(unittest.TestCase):
    def test_custom_codex_home_and_allowlist(self) -> None:
        with tempfile.TemporaryDirectory() as home:
            configured = Path(home) / "private-codex-home"
            env = os.environ.copy()
            env["HOME"] = home
            env["CODEX_HOME"] = str(configured)
            result = subprocess.run(
                [sys.executable, str(SCRIPT)],
                input=json.dumps(
                    {
                        "cwd": "/project",
                        "session_id": "session-1",
                        "model": "omit",
                        "secret": "omit",
                    }
                ),
                text=True,
                capture_output=True,
                env=env,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            path = configured / "team-logs/session-events.jsonl"
            record = json.loads(path.read_text(encoding="utf-8").splitlines()[0])
            self.assertEqual(
                record["payload"],
                {"cwd": "/project", "session_id": "session-1"},
            )

    def test_malformed_input_is_fail_open(self) -> None:
        with tempfile.TemporaryDirectory() as home:
            env = os.environ.copy()
            env["HOME"] = home
            env.pop("CODEX_HOME", None)
            result = subprocess.run(
                [sys.executable, str(SCRIPT)],
                input="{bad",
                text=True,
                capture_output=True,
                env=env,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            path = Path(home) / ".codex/team-logs/session-events.jsonl"
            record = json.loads(path.read_text(encoding="utf-8").splitlines()[0])
            self.assertEqual(record["payload"], {})


if __name__ == "__main__":
    unittest.main()
