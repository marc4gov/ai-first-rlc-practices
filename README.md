# AI-First Runtime LifeCycle (RLC) Practices

A comprehensive framework for AI agent teams handling production runtime operations: observing, monitoring, alerting, and controlling systems when things go south.

## Overview

This is the Runtime LifeCycle companion to [ai-first-sdlc-practices](https://github.com/SteveGJones/ai-first-sdlc-practices). While SDLC focuses on building software right, RLC focuses on **running software right** in production.

### Philosophy

Production runtime is a continuous cycle of:
1. **Observe** - Collect telemetry from systems
2. **Monitor** - Evaluate against expected behavior
3. **Alert** - Notify when intervention needed
4. **Control** - Execute remediation actions
5. **Learn** - Improve from incidents

## What RLC Provides

### Agent Teams for Runtime Operations

- **Observers**: Metrics collection, log aggregation, event streaming
- **Monitors**: Threshold evaluation, anomaly detection, health checks
- **Alerters**: Alert routing, escalation management, on-call coordination
- **Controllers**: Auto-remediation, circuit breakers, graceful degradation
- **Responders**: Runbook execution, war room coordination, post-mortem
- **Communication**: Event routing, agent handoffs, status broadcasts

### Event Handling Module

The core runtime event handling system:
- **Event Ingestion** - Webhooks, queues, streams
- **Event Routing** - Direct events to appropriate agents
- **Event Correlation** - Aggregate related events
- **State Machine** - Track incident lifecycle

### RLC Gates

Mandatory checkpoints for runtime operations:
- **Detection Gate** - Issue detected → classified
- **Triage Gate** - Assessed → response planned
- **Response Gate** - Action taken → monitoring recovery
- **Resolution Gate** - Verified → post-mortem created

### Templates

- Runbooks for common incidents
- SLO/SLI definitions
- Alert configurations
- Post-mortem documents
- Event schemas

## Quick Start

```bash
# Clone the repository
git clone https://github.com/your-org/ai-first-rlc-practices.git
cd ai-first-rlc-practices

# Set up the framework
./setup.sh

# Launch Claude with RLC context
./bin/claude
```

## Documentation

- [CLAUDE-CORE.md](CLAUDE-CORE.md) - Core framework instructions
- [CLAUDE-SETUP.md](CLAUDE-SETUP.md) - Setup guide
- [AGENT-INDEX.md](AGENT-INDEX.md) - Complete agent catalog
- [EVENT-HANDLING.md](docs/EVENT-HANDLING.md) - Event module guide
- [RLC-GATES.md](docs/RLC-GATES.md) - Gates configuration
- [RUNBOOKS.md](docs/RUNBOOKS.md) - Runbook templates

## Agent Categories

| Category | Purpose | Example Agents |
|----------|---------|----------------|
| **Observers** | Collect telemetry | metrics-collector, log-aggregator, event-streamer |
| **Monitors** | Evaluate health | threshold-evaluator, anomaly-detector, health-checker |
| **Alerters** | Route notifications | alert-router, escalation-manager, on-call-coordinator |
| **Controllers** | Execute actions | auto-remediator, circuit-breaker, graceful-degrader |
| **Responders** | Handle incidents | incident-commander, runbook-executor, post-mortem-writer |

## RLC vs SDLC

| Aspect | SDLC | RLC |
|--------|------|-----|
| **Focus** | Building software | Running software |
| **Timeline** | Design → Deploy | Deploy → Operate |
| **Agents** | Architects, developers, testers | Observers, monitors, responders |
| **Gates** | Requirements → Design → Implementation → Review | Detection → Triage → Response → Resolution |
| **Documents** | Architecture, ADRs, traceability | Runbooks, SLOs, post-mortems |
| **Validation** | Code quality, test coverage | SLO compliance, MTTR |

## Contributing

This framework follows the same principles as ai-first-sdlc-practices:
- Team-first agent collaboration
- Zero tolerance for shortcuts
- Comprehensive documentation
- Continuous validation

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

MIT License - See [LICENSE](LICENSE) for details.

## Related Projects

- [ai-first-sdlc-practices](https://github.com/SteveGJones/ai-first-sdlc-practices) - SDLC framework
- [agent-sdk-python](https://github.com/anthropics/agent-sdk-python) - Agent SDK for Python

---

**Remember**: Production runtime is where software meets reality. RLC ensures your systems survive that encounter.
