# Contributing to AI-First RLC Practices

Thank you for your interest in contributing to the AI-First Runtime LifeCycle (RLC) Practices framework! This document provides guidelines for contributing to this project, whether you're a human developer or an AI agent.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for all contributors, regardless of whether they are human or AI-assisted.

## Getting Started

### For Human Contributors

1. **Fork the repository** and clone it locally
2. **Run the setup**: `./setup.sh`
3. **Create a feature branch**: `git checkout -b feature/your-contribution`
4. **Read CLAUDE-CORE.md**: Understand the RLC framework and agent collaboration model

### For AI Agents

When asked to contribute to this project:
1. Follow the instructions in CLAUDE-CORE.md
2. Always create incident documentation for production changes
3. Update runbooks when introducing new procedures
4. Never push directly to main

## Contribution Process

### 1. Create a Proposal (REQUIRED)

Before implementing any changes to the framework:

```bash
# For framework changes
Create a document in: docs/proposals/XXX-your-proposal.md
```

Your proposal should include:
- Clear problem statement
- Proposed solution
- Impact on existing agents and runbooks
- Testing approach
- Runtime safety considerations

### 2. Get Feedback

- Open a draft PR with just your proposal
- Label it with `proposal`
- Wait for maintainer feedback before implementing

### 3. Implementation

Follow the RLC framework workflow:

```bash
# Create feature branch
git checkout -b feature/your-feature

# Work on implementation
# ... make changes ...

# Validate your work
python tools/validation/validate-events.py
python tools/validation/validate-runbooks.py

# Test agent configurations
python tools/validation/check-incident-debt.py
```

### 4. Testing Requirements

All contributions must include:
- Validation scripts for new event types
- Runbook templates for new procedures
- Documentation updates
- Example configurations where applicable

### 5. Pull Request Process

#### PR Checklist
- [ ] Proposal exists and was discussed
- [ ] All validation scripts pass
- [ ] Documentation is updated
- [ ] Runbooks are created/updated for new procedures
- [ ] Agent configurations tested
- [ ] Commit messages follow conventional format

#### PR Title Format
```
<type>: <description>

Types: feat, fix, docs, style, refactor, test, chore
```

Examples:
- `feat: add WASM observability support`
- `fix: correct event routing for SEV1 incidents`
- `docs: improve agent model selection guide`

## Testing

### Running Validation

```bash
# Validate event configuration
python tools/validation/validate-events.py

# Validate runbooks
python tools/validation/validate-runbooks.py

# Check for incident debt
python tools/validation/check-incident-debt.py

# Validate RLC gates
python tools/validation/validate-gates.py
```

### Testing Agent Configurations

```bash
# Test with budget tier
python tools/wizard/rlc-setup-wizard.py --tier budget

# Test with balanced tier
python tools/wizard/rlc-setup-wizard.py --tier balanced

# Test with premium tier
python tools/wizard/rlc-setup-wizard.py --tier premium
```

## Documentation Standards

### Agent Documentation

When creating new agents:
- Use the agent template in `agents/agent-template.md`
- Include: purpose, inputs, outputs, model recommendations, MCP servers
- Add to AGENT-INDEX.md

### Runbook Documentation

When creating new runbooks:
- Use templates in `templates/runbooks/`
- Include: trigger conditions, steps, rollback, verification
- Test runbook validation before committing

### Event Documentation

When adding new event types:
- Update docs/EVENT-HANDLING.md
- Add event type to the standard types table
- Include routing rules and examples

## Workflow for Different Contribution Types

### Adding New Agent Types

1. Create proposal: `docs/proposals/XXX-new-agent-type.md`
2. Create agent definition: `agents/<category>/<agent-name>.md`
3. Add model recommendations: Update `docs/agent-model-advisory.md`
4. Add to AGENT-INDEX.md
5. Create example configuration

### Adding New Event Sources

1. Create proposal documenting the source
2. Add ingestion method to `events/ingestion/`
3. Add routing rule to `events/routing/`
4. Update EVENT-HANDLING.md
5. Add validation tests

### Improving Agent Model Selection

1. Research model capabilities for the agent's task
2. Update `docs/agent-model-advisory.md`
3. Update `.rlc/config/agent-models-template.yaml`
4. Test with all three tiers
5. Document rationale

### Adding MCP Server Integration

1. Document the MCP server and its capabilities
2. Update agent definitions with MCP server requirements
3. Add to `.rlc/config/mcp-servers-template.yaml`
4. Test server connectivity
5. Document permissions and security considerations

## Reporting Issues

### Bug Reports Should Include
- Framework version (see VERSION file)
- Python version
- Operating system
- Event/Agent configuration
- Steps to reproduce
- Expected vs actual behavior
- Error messages/logs

### Feature Requests Should Include
- Use case description
- Which agent types would benefit
- Proposed solution
- Alternative approaches considered
- Impact on existing users

## Architecture Decisions

Major changes require an Architecture Decision Record (ADR):

```bash
cp templates/adr/template-adr.md docs/adr/XXX-decision-title.md
```

## Security

- Never commit secrets or API credentials
- Report security issues privately to maintainers
- Follow secure coding practices for runtime operations
- Document security implications of auto-remediation actions
- Use principle of least privilege for MCP server permissions

## Commit Message Guidelines

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types
- **feat**: New agent, event type, or feature
- **fix**: Bug fix in event handling or agent behavior
- **docs**: Documentation only
- **style**: Formatting, missing semicolons, etc.
- **refactor**: Code change that neither fixes a bug nor adds a feature
- **test**: Adding missing validation tests
- **chore**: Maintenance tasks

### Examples
```
feat(observers): add WASM telemetry collector

- Add support for WebAssembly module telemetry
- Include memory and performance metrics
- Integrate with existing metrics pipeline

Closes #123
```

```
fix(events): correct incident state transitions

- Fix triaging → responding transition
- Add missing gate validation
- Update documentation

Fixes #456
```

## AI Agent Contributions

AI agents are first-class contributors to this project. When contributing via AI:

1. **Identify yourself**: Include "AI-assisted" in PR description
2. **Follow all rules**: Same standards apply to all contributors
3. **Document your process**: Help us improve AI workflows
4. **Report AI-specific issues**: Help us enhance AI ergonomics

## Recognition

All contributors will be recognized in:
- GitHub contributors graph
- Release notes
- Framework documentation

## Getting Help

- **Documentation**: Start with CLAUDE-CORE.md
- **Agent Catalog**: See AGENT-INDEX.md
- **Examples**: Check examples/ directory
- **Issues**: Search existing issues first
- **Discussions**: Use GitHub Discussions for questions

## Continuous Improvement

This contribution guide itself follows RLC practices:
- Propose changes via proposal
- Document what works/doesn't work
- Help us improve the contribution process
- Create post-mortems after incidents

## RLC-Specific Guidelines

### Zero Incident Debt Policy

Every production change that affects runtime behavior must:
1. Document potential failure modes
2. Include rollback procedures
3. Have monitoring/alerting in place
4. Create or update runbooks

### Agent Model Selection

When contributing agent model recommendations:
- Prioritize open-source, self-hostable models
- Consider resource requirements for each tier
- Document latency vs accuracy tradeoffs
- Test models before recommending

### MCP Server Integration

When adding MCP server support:
- Document required permissions
- Include security considerations
- Provide example configurations
- Test with all supported platforms

---

**Remember**: The RLC framework runs in production. Your changes affect real systems when things go wrong. Quality and safety are paramount. When in doubt, ask!
