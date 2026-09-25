#!/usr/bin/env python3
"""Regression tests for the fail-open subagent lifecycle hook."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).with_name("subagent_lifecycle.py")
MAX_LOG_BYTES = 1_048_576


class SubagentLifecycleTest(unittest.TestCase):
    def run_hook(
        self, raw_input: str, *, codex_home: Path | None = None
    ) -> tuple[subprocess.CompletedProcess[str], dict | None]:
        with tempfile.TemporaryDirectory() as home:
            env = os.environ.copy()
            env["HOME"] = home
            env.pop("CODEX_HOME", None)
            if codex_home is not None:
                env["CODEX_HOME"] = str(codex_home)
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "start"],
                input=raw_input,
                text=True,
                capture_output=True,
                env=env,
                check=False,
            )
            selected_home = codex_home or Path(home) / ".codex"
            log_path = selected_home / "team-logs/subagent-events.jsonl"
            record = None
            if log_path.exists():
                record = json.loads(
                    log_path.read_text(encoding="utf-8").splitlines()[-1]
                )
            return result, record

    def test_non_object_json_is_treated_as_empty_payload(self) -> None:
        for raw_input in ("[]", "null", '"text"', "42"):
            with self.subTest(raw_input=raw_input):
                result, record = self.run_hook(raw_input)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIsNotNone(record)
                self.assertEqual(record["payload"], {})

    def test_malformed_json_is_treated_as_empty_payload(self) -> None:
        result, record = self.run_hook("{bad")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIsNotNone(record)
        self.assertEqual(record["payload"], {})

    def test_payload_drops_model_and_secret_fields(self) -> None:
        result, record = self.run_hook(
            '{"agent_id":"agent-1","model":"unlogged","secret":"drop"}'
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIsNotNone(record)
        self.assertEqual(record["payload"], {"agent_id": "agent-1"})

    def test_configured_codex_home_is_used(self) -> None:
        with tempfile.TemporaryDirectory() as home:
            configured = Path(home) / "custom-codex"
            result, record = self.run_hook("{}", codex_home=configured)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIsNotNone(record)
            self.assertTrue(
                (configured / "team-logs/subagent-events.jsonl").is_file()
            )

    def test_rotation_creates_a_persistent_sidecar_lock_file(self) -> None:
        with tempfile.TemporaryDirectory() as home:
            log_dir = Path(home) / ".codex/team-logs"
            log_dir.mkdir(parents=True)
            log_path = log_dir / "subagent-events.jsonl"
            log_path.write_text("x" * MAX_LOG_BYTES, encoding="utf-8")

            env = os.environ.copy()
            env["HOME"] = home
            env.pop("CODEX_HOME", None)
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "start"],
                input="{}",
                text=True,
                capture_output=True,
                env=env,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(
                log_path.with_name(f"{log_path.name}.lock").is_file(),
                "rotation must serialize through a persistent sidecar lock file",
            )
            self.assertTrue(log_path.with_name(f"{log_path.name}.1").is_file())

    def test_concurrent_events_are_not_lost_or_interleaved(self) -> None:
        with tempfile.TemporaryDirectory() as home:
            env = os.environ.copy()
            env["HOME"] = home
            env.pop("CODEX_HOME", None)

            def invoke(index: int) -> subprocess.CompletedProcess[str]:
                return subprocess.run(
                    [sys.executable, str(SCRIPT), "start"],
                    input=json.dumps({"agent_id": f"agent-{index}"}),
                    text=True,
                    capture_output=True,
                    env=env,
                    check=False,
                )

            with ThreadPoolExecutor(max_workers=12) as executor:
                results = list(executor.map(invoke, range(24)))

            self.assertTrue(
                all(result.returncode == 0 for result in results),
                [result.stderr for result in results if result.returncode],
            )
            log_path = Path(home) / ".codex/team-logs/subagent-events.jsonl"
            records = [
                json.loads(line)
                for line in log_path.read_text(encoding="utf-8").splitlines()
            ]
            ids = {record["payload"]["agent_id"] for record in records}
            self.assertEqual(ids, {f"agent-{index}" for index in range(24)})

    def test_unavailable_log_path_is_fail_open(self) -> None:
        with tempfile.TemporaryDirectory() as home:
            blocked = Path(home) / "not-a-directory"
            blocked.write_text("file", encoding="utf-8")
            env = os.environ.copy()
            env["HOME"] = home
            env["CODEX_HOME"] = str(blocked)

            result = subprocess.run(
                [sys.executable, str(SCRIPT), "start"],
                input="{}",
                text=True,
                capture_output=True,
                env=env,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
