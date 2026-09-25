# Design Overview

## Purpose

This repository provides a model-neutral Codex workflow for software delivery, platform operations, and independent review. It uses project-local custom agent profiles, an optional plugin, reusable skills, guarded hooks and shell rules, and spec templates.

Codex selects the active model and reasoning behavior from the current app or session configuration. Custom agent files omit model and reasoning overrides so they inherit the current session defaults.

## Roles

| Role | Responsibility |
| --- | --- |
| Main thread | Owns user communication, scope, decisions, integration, and final verification. |
| fullstack-agent | Plans durable work, splits file-disjoint tasks, coordinates workers, and consolidates evidence. |
| coding-agent | Implements bounded application, test, and tooling changes. |
| devops-agent | Reviews and implements platform, CI/CD, infrastructure, reliability, security, observability, performance, cost, and operations work. |
| review-agent | Independently reviews correctness, security, regressions, and verification evidence. |

The built-in Codex explorer role is useful for read-only repository mapping. It is not a substitute for the independent reviewer or the main thread's verification.

## Workflow

1. Record durable requirements, design, tasks, decisions, and review history under .codex/specs/<slug>/.
2. Split implementation into small waves with file-disjoint ownership.
3. Delegate only work that can progress independently; keep the main thread responsible for integration.
4. Verify outputs with focused tests, static checks, and safe executable equivalents.
5. Run an independent adversarial review for each required task group.
6. Track live validation separately when it requires deployment or shared resources.

Each durable task group has a non-resetting review limit of three cycles. Cycle 3 is terminal.

## Agentic Security

When a workflow gives agents tools, external authority, persistent context, or inter-agent communication, assess the applicable risks in the OWASP Top 10 for Agentic Applications. Consider the OWASP Agent Control Standard as a runtime control and observability design reference when supported. Record concrete controls and evidence in the spec or review. Treat NIST agent standards work as evolving guidance; do not claim compliance or certification.

## Configuration Boundaries

- Custom agents live in .codex/agents/*.toml.
- Project concurrency uses the current agents.max_concurrent_threads_per_session setting.
- This sample does not set a model, reasoning effort, provider, or credentials.
- Plugin skills load on demand; a new thread may be needed after changing agent or plugin files.
- Hooks and command rules are project-local examples and require trust and review.
