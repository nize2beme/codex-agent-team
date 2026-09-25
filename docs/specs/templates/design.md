# Design: <Title>

> Architecture, repository structure, platform, infrastructure, and operational design for <slug>.

## Architecture Overview

Describe components, trust boundaries, dependencies, and request or data flow. Link diagrams when useful.

## Repository / Module Structure

    <tree of directories and key files this work will create or touch>

## Components

### <Component Name>

- Responsibility:
- Interface and data flows:
- Dependencies and owners:

## Data And State

Describe schemas, storage, retention, classification, backup, recovery, and migration where relevant.

## Platform And Delivery

Describe selected platform, infrastructure as code, environments, identity, CI/CD, deployment, health checks, rollback, and outputs consumed by other components.

## Security Considerations

For agentic or production-impacting work, identify applicable threats and controls. Use the OWASP agentic threat taxonomy where agents or tools can affect state.

- Authentication and authorization
- Least privilege and secrets
- Encryption and network boundaries
- Logging, retention, and privacy
- Input and output validation
- Recovery and audit evidence

## Tradeoffs And Alternatives

Record rejected options and the reason.

## Open Design Questions

- [ ] <question>
