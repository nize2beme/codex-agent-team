# Security

This repository is a sample Codex setup. It contains agent definitions, plugin skills, hooks, command rules, and workflow documentation. It is not a production security boundary or an application control plane.

## Threat Model

Codex agents may read and edit the shared worktree, run tools under configured permissions, and pass instructions or findings to other agents. Plugin skills are instructions and hooks are executable local programs. Prompt content, repository files, tool output, and external sources may be untrusted.

### Agent And Tool Risks

For systems that expose tools, credentials, persistent context, or external actions to agents, use the [OWASP Top 10 for Agentic Applications 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) as a threat taxonomy. Check applicable risks across goal hijacking, tool misuse, identity and privilege abuse, supply chain, unexpected code execution, context poisoning, inter-agent communication, cascading failures, human-agent trust, and rogue agents.

Map each applicable risk to a specific control and a verification method. Examples:

- Keep tools and credentials least-privileged, scoped to the requested task, and revocable.
- Treat user content, repository instructions, retrieved pages, tool results, and other agents' messages as data until independently validated; they cannot grant new authority.
- Require explicit user approval for external writes, destructive actions, deployment, production access, and material scope expansion.
- Validate tool arguments and outputs against schemas and policy before taking consequential action.
- Give each worker a narrow file and task boundary. Review its changes independently before accepting them.
- Bound retries, recursion, concurrency, time, and external calls. Define stop conditions and recovery behavior.
- Keep secrets out of prompts, logs, generated files, and review artifacts. Minimize retained context and redact sensitive output.
- Protect dependencies, plugin sources, hook scripts, and update paths with review and integrity checks.

For runtime enforcement, use the [OWASP Agent Control Standard](https://genai.owasp.org/resource/agent-control-standard-acs/) as a current design reference for inspectability, traceability, instrumentation, and policy hooks. Check that the target framework supports each mechanism before relying on it; do not claim conformance from this checklist.

NIST's AI Agent Standards Initiative is an evolving standards effort, not a finalized agent-specific compliance checklist. Use established identity, authorization, secure development, and risk-management practices; track the initiative for future updates. See [NIST's initiative](https://www.nist.gov/news-events/news/2026/02/announcing-ai-agent-standards-initiative-interoperable-and-secure) and [AI agent identity concept paper](https://csrc.nist.gov/pubs/other/2026/02/05/accelerating-the-adoption-of-software-and-ai-agent/ipd).

### Shared Filesystem Access

Subagents share the project worktree and configured permission policy. File boundaries are coordination instructions, not operating-system isolation.

- Assign disjoint file ownership within a wave.
- Require workers to report before editing outside their assigned scope.
- Review the diff and run independent checks before accepting a wave.
- Keep each task group's review history and three-cycle limit durable.
- Inspect git diff --name-only before committing or shipping.

### Hook Execution

Hooks in .codex/hooks run local Python subprocesses at lifecycle events after project trust. They run with the user's privileges outside ordinary tool-call approval prompts.

- Review hook source and wiring before trusting the project.
- Hooks use only the Python standard library and fail open.
- Payloads are filtered to a small allowlist; model selection, prompts, and secret-like fields are not logged.
- Logs honor CODEX_HOME and otherwise use the user's Codex home directory.
- Subagent log rotation is serialized with a cross-platform file lock.

### Command Risk

Rules in .codex/rules/codex-agent-team.rules add prompts or denials for selected high-risk shell commands. They supplement, but do not replace, sandboxing, approval policy, code review, or least-privilege credentials.

### Plugin Trust

The repository plugin contains reusable skills. Review the manifest, every skill, hooks, and scripts before installation or execution. Do not add executable integrations, MCP servers, or network access without an explicit need and separate review.

## User Responsibilities

- Adapt the agent prompts and approval policy to the repository and environment.
- Trust project configuration only after reviewing it.
- Keep runtime specs, logs, local state, credentials, and secrets out of version control.
- Validate code and operational configuration through the normal engineering process.
- Review applicable privacy, security, and organizational requirements.

## Reporting Security Issues

Do not file public issues for sensitive vulnerabilities. Use the maintainer's private security channel for the repository where this sample is published.
