---
name: agentic-security-review
description: Use when an agent, tool, plugin, workflow, or automated action can access sensitive context, credentials, code execution, or external state.
---

# Agentic Security Review

## Outcome

Map agent authority and trust boundaries to concrete threats, controls, tests, and residual risks. Use this skill for agent-enabled or agent-managed systems, not routine software with no agent authority surface.

Use the OWASP Top 10 for Agentic Applications 2026 as a threat taxonomy. It is a review aid, not a pass/fail certification standard.

For runtime policy and observability, consider the OWASP Agent Control Standard as a design reference for inspectable agents, traceable actions, instrumentation, and middleware-enforced policies. Verify that the selected runtime implements the controls you rely on; do not assume conformance.

## Review Method

1. Draw the authority path: user, coordinator, role agent, plugin or tool, credential, target system, persistent memory, logs, and resulting state change.
2. Mark which inputs are untrusted, who can authorize actions, and where tool outputs or inter-agent messages are checked.
3. Select applicable OWASP agentic risks and record an attack path, control, test or evidence, owner, and residual risk for each.
4. Verify controls against code and configuration. A prompt claim alone does not prove enforcement.
5. Require explicit user approval for external writes, destructive actions, deployment, production access, or broader authority.
6. State untested behavior and recovery steps; do not infer a secure result from missing evidence.

## Threat Areas

Consider all ten OWASP categories and include only those relevant to the design:

| Risk | Review focus |
| --- | --- |
| ASI01 Agent Goal Hijack | Can hostile content change the goal or smuggle instructions through retrieved data? |
| ASI02 Tool Misuse and Exploitation | Are tools allowlisted, arguments validated, and authority limited to the task? |
| ASI03 Identity and Privilege Abuse | Are identity, tokens, and delegation scoped, attributable, and revocable? |
| ASI04 Agentic Supply Chain | Are plugins, tool servers, workflows, dependencies, and updates reviewed and integrity-checked? |
| ASI05 Unexpected Code Execution | Can generated or injected input reach a shell, code interpreter, or build runner without controls? |
| ASI06 Memory and Context Poisoning | Can untrusted data persist, alter later decisions, or be mistaken for trusted policy? |
| ASI07 Insecure Inter-Agent Communication | Are handoffs narrow, structured, attributable, and prevented from granting new authority? |
| ASI08 Cascading Failures | Are concurrency, retries, recursion, time, cost, and downstream effects bounded? |
| ASI09 Human-Agent Trust Exploitation | Are uncertainty, provenance, approvals, and consequential changes visible to the user? |
| ASI10 Rogue Agents | Can behavior be observed, constrained, interrupted, and recovered without uncontrolled authority? |

## Baseline Controls

- Separate instruction from data; treat repository content, retrieved pages, and tool output as untrusted until checked.
- Enforce least privilege outside the prompt where the platform supports it; keep consequential actions behind an approval boundary.
- Validate arguments, output schemas, destination identities, and state changes.
- Make handoffs carry provenance, exact scope, evidence, and explicit authorization limits.
- Bound recursion, fan-out, retries, deadlines, and cost. Define a terminal stop condition.
- Minimize sensitive context and logs; redact credentials and personal data.
- Review plugin and dependency sources and their update path.
- Include a test that attempts a relevant misuse path, plus recovery evidence for consequential workflows.

## Output

Write an Agentic Security Review into the project's security or review artifact:

| Threat / attack path | Control | Test or evidence | Owner | Residual risk |
| --- | --- | --- | --- | --- |

Cite the current OWASP material and official platform documentation. NIST's AI Agent Standards Initiative is evolving; use established identity, authorization, secure-development, and risk-management controls without claiming agent-standard conformance.
