#!/usr/bin/env python3
"""Repository invariants for the model-neutral Codex DevOps workflow."""

from __future__ import annotations

import json
import re
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CODEX = ROOT / ".codex"
PLUGIN = ROOT / "plugins" / "codex-agent-team"
EXPECTED_AGENTS = {
    "coding-agent",
    "devops-agent",
    "fullstack-agent",
    "review-agent",
}
EXPECTED_SKILLS = {
    "agentic-security-review",
    "concurrent-cached-fetch",
    "git-workflow",
    "optimize-my-codex",
    "team-brainstorm",
    "team-coordination",
    "team-documentation",
    "team-review-cycle",
    "team-spec-workflow",
}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class RepositoryInvariantTests(unittest.TestCase):
    maxDiff = None

    def test_current_model_neutral_agent_configuration(self) -> None:
        files = sorted((CODEX / "agents").glob("*.toml"))
        self.assertEqual({path.stem for path in files}, EXPECTED_AGENTS)
        for path in files:
            with self.subTest(agent=path.stem):
                data = tomllib.loads(read(path))
                self.assertEqual(data["name"], path.stem)
                self.assertTrue(data.get("description"))
                self.assertTrue(data.get("developer_instructions"))
                self.assertLessEqual(
                    set(data),
                    {"name", "description", "developer_instructions", "sandbox_mode"},
                )

        config = tomllib.loads(read(CODEX / "config.toml"))
        self.assertEqual(
            config["agents"]["max_concurrent_threads_per_session"], 8
        )
        self.assertNotIn("model", config)
        self.assertTrue(
            config["plugins"]["codex-agent-team@sample-codex-agent-team"]["enabled"]
        )

    def test_portable_plugin_and_local_marketplace_agree(self) -> None:
        manifest_path = PLUGIN / "plugin.json"
        manifest = json.loads(read(manifest_path))
        self.assertEqual(manifest["name"], "codex-agent-team")
        self.assertIn("com.openai", manifest["extensions"])
        self.assertEqual(
            set(manifest),
            {
                "$schema", "name", "version", "description", "author",
                "license", "keywords", "extensions",
            },
        )

        marketplace = json.loads(read(ROOT / ".agents/plugins/marketplace.json"))
        entry = next(
            item for item in marketplace["plugins"]
            if item["name"] == "codex-agent-team"
        )
        plugin_path = ROOT / entry["source"]["path"]
        self.assertTrue((plugin_path / "plugin.json").is_file())
        self.assertEqual(plugin_path.resolve(), PLUGIN.resolve())

    def test_skill_sources_and_discovery_metadata(self) -> None:
        skill_dirs = {
            path.name for path in (PLUGIN / "skills").iterdir() if path.is_dir()
        }
        self.assertEqual(skill_dirs, EXPECTED_SKILLS)
        for name in sorted(EXPECTED_SKILLS):
            with self.subTest(skill=name):
                skill = PLUGIN / "skills" / name
                text = read(skill / "SKILL.md")
                self.assertRegex(text, r"(?m)^---\s*\nname: ")
                self.assertIn("description:", text.split("---", 2)[1])
                metadata = read(skill / "agents/openai.yaml")
                for key in ("display_name:", "short_description:", "default_prompt:"):
                    self.assertIn(key, metadata)

    def test_devops_review_and_agentic_security_are_integrated(self) -> None:
        self.assertTrue((ROOT / "docs/specs/templates/devops-review.md").is_file())
        self.assertIn(
            "agentic-security-review",
            read(CODEX / "agents/review-agent.toml"),
        )
        self.assertIn(
            "agentic-security-review",
            read(PLUGIN / "skills/team-spec-workflow/SKILL.md"),
        )
        self.assertIn("OWASP Top 10", read(ROOT / "SECURITY.md"))
        self.assertIn("Agent Control Standard", read(ROOT / "SECURITY.md"))
        self.assertIn("NIST", read(ROOT / "SECURITY.md"))

    def test_hooks_are_configured_for_supported_platforms(self) -> None:
        hooks = json.loads(read(CODEX / "hooks.json"))["hooks"]
        for event, groups in hooks.items():
            with self.subTest(event=event):
                command = groups[0]["hooks"][0]
                self.assertIn("command", command)
                self.assertIn("commandWindows", command)

        for name in ("session_start.py", "subagent_lifecycle.py"):
            source = read(CODEX / "hooks" / name)
            self.assertIn("CODEX_HOME", source)
            self.assertNotIn('"model"', source)

    def test_docs_use_current_role_names_and_settings(self) -> None:
        text = "\n".join(
            read(path)
            for path in (
                ROOT / "README.md",
                ROOT / "AGENTS.md",
                ROOT / "docs/design.md",
                ROOT / "docs/specs/templates/tasks.md",
            )
        )
        self.assertIn("devops-agent", text)
        self.assertIn("max_concurrent_threads_per_session", text)
        self.assertIn("explorer", text)

    def test_removed_provider_and_version_specific_content(self) -> None:
        pieces = [
            "a" + "w" + "s",
            "ama" + "zon",
            "cloud" + "formation",
            "cloud" + "watch",
            "k" + "ms",
            "e" + "ks",
            "ar" + "n",
            "well" + "-architected",
            "solutions" + " architect",
        ]
        banned = re.compile(
            r"|".join(
                rf"(?<![a-z0-9]){re.escape(term)}(?![a-z0-9])"
                for term in pieces
            ),
            re.IGNORECASE,
        )
        violations: list[str] = []
        for path in ROOT.rglob("*"):
            if not path.is_file() or any(part in {".git", "__pycache__"} for part in path.parts):
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            for number, line in enumerate(text.splitlines(), start=1):
                if banned.search(line):
                    violations.append(f"{path.relative_to(ROOT)}:{number}: {line.strip()}")
        self.assertEqual(violations, [])

    def test_review_cycles_are_group_scoped_and_bounded(self) -> None:
        sources = [
            ROOT / "AGENTS.md",
            ROOT / "README.md",
            ROOT / "docs/specs/templates/review.md",
            PLUGIN / "skills/team-review-cycle/SKILL.md",
            PLUGIN / "skills/team-spec-workflow/SKILL.md",
        ]
        for path in sources:
            with self.subTest(path=path.relative_to(ROOT)):
                text = read(path).lower()
                self.assertIn("task group", text)
                self.assertIn("cycle 3", text)
                self.assertTrue("group id" in text or "group identifier" in text or "identifier" in text)
                self.assertTrue(
                    "non-resetting" in text or "do not reset" in text
                )

    def test_all_current_references_resolve(self) -> None:
        paths = [
            ROOT / "README.md",
            ROOT / "AGENTS.md",
            ROOT / "docs/design.md",
        ]
        missing = []
        for path in paths:
            text = read(path)
            for match in re.findall(r"docs/specs/templates/[A-Za-z0-9_-]+\.md", text):
                if not (ROOT / match).is_file():
                    missing.append(f"{path.relative_to(ROOT)} -> {match}")
        self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()
