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

### AI Model Recommendations

Per-agent open-source model recommendations for local deployment:
- **Budget Tier**: 3-4B models (8GB VRAM, <$50/month)
- **Balanced Tier**: 3-7B models (16GB VRAM, $50-150/month)
- **Premium Tier**: 3-14B+ models (32GB VRAM, $200-1000+/month)

Supported models: Llama, Mistral, Qwen, Phi, Mixtral

## Quick Start

### For Users: Setting Up RLC for Your Runtime

**Step 1:** Open your infrastructure repository where you want to implement RLC practices.

**Step 2:** Give Claude this prompt:
```
I want to set up the AI-First RLC framework from https://github.com/your-org/ai-first-rlc-practices for my production runtime.
```

Claude will ask you about your workload type and hosting preferences, then:
1. Analyze your codebase for languages, frameworks, deployment configs
2. Prescribe event handling stack and agent team configuration
3. Generate setup artifacts in `./rlc-setup/`
4. Run the Construction Agent to build infrastructure
5. Configure AI models and MCP servers for each agent

See [QUICKSTART.md](QUICKSTART.md) for detailed step-by-step instructions.

### For Framework Contributors

```bash
# Clone the repository
git clone https://github.com/your-org/ai-first-rlc-practices.git
cd ai-first-rlc-practices

# Run the setup
./setup.sh

# Read the core instructions
cat CLAUDE-CORE.md
```

## Documentation

### Essential Guides

- **[CLAUDE-CORE.md](CLAUDE-CORE.md)** - Core framework instructions for agent teams
- **[CLAUDE-SETUP.md](CLAUDE-SETUP.md)** - Setup and configuration guide
- **[QUICKSTART.md](QUICKSTART.md)** - Get started in minutes
- **[AGENT-INDEX.md](AGENT-INDEX.md)** - Complete agent catalog

### Module Documentation

- **[docs/EVENT-HANDLING.md](docs/EVENT-HANDLING.md)** - Event handling system guide
- **[docs/agent-model-advisory.md](docs/agent-model-advisory.md)** - AI model selection guide

### Contribution

- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contribution guidelines
- **[CHANGELOG.md](CHANGELOG.md)** - Version history and changes

## Agent Categories

| Category | Purpose | Example Agents |
|----------|---------|----------------|
| **Observers** | Collect telemetry | metrics-collector, log-aggregator, event-streamer |
| **Monitors** | Evaluate health | threshold-evaluator, anomaly-detector, health-checker |
| **Alerters** | Route notifications | alert-router, escalation-manager, on-call-coordinator |
| **Controllers** | Execute actions | auto-remediator, circuit-breaker, graceful-degrader |
| **Responders** | Handle incidents | incident-commander, runbook-executor, post-mortem-writer |

See [AGENT-INDEX.md](AGENT-INDEX.md) for the complete catalog of 10+ agents.

## RLC vs SDLC

| Aspect | SDLC | RLC |
|--------|------|-----|
| **Focus** | Building software | Running software |
| **Timeline** | Design → Deploy | Deploy → Operate |
| **Agents** | Architects, developers, testers | Observers, monitors, responders |
| **Gates** | Requirements → Design → Implementation → Review | Detection → Triage → Response → Resolution |
| **Documents** | Architecture, ADRs, traceability | Runbooks, SLOs, post-mortems |
| **Validation** | Code quality, test coverage | SLO compliance, MTTR |

## Event Handling Stack

The RLC framework supports three tiers of event handling infrastructure:

### Budget Tier (Self-Hosted)
- **Prometheus** + **Grafana** (self-hosted)
- **Loki** for logs
- **Jaeger** for tracing
- **Tempo** for trace storage
- Cost: <$50/month
- Best for: Development, resource-constrained environments

### Balanced Tier (Managed)
- **Grafana Cloud** or **Datadog**
- Managed metrics, logs, and traces
- Cost: $50-150/month
- Best for: Production workloads

### Premium Tier (Enterprise)
- **Splunk** + **New Relic** + **Datadog**
- Enterprise-grade observability
- Cost: $200-1000+/month
- Best for: Mission-critical systems

## Supported Technologies

### Languages
- Python, JavaScript/TypeScript, Go, Java, Ruby, Rust, WebAssembly

### Platforms
- Kubernetes, Docker, Serverless (AWS Lambda, GCP Cloud Run), VM, PaaS

### Cloud Providers
- AWS, GCP, Azure, Hetzner, Scaleway, OVHcloud, DigitalOcean

### Observability Tools
- Prometheus, Grafana, Loki, Jaeger, Tempo, Datadog, New Relic, Splunk

## Project Structure

```
rlc/
├── agents/              # Runtime agent definitions
│   ├── core/           # Core runtime agents
│   ├── observers/      # Telemetry collection
│   ├── monitors/       # Health evaluation
│   ├── alerters/       # Notification routing
│   ├── controllers/    # Remediation actions
│   └── responders/     # Incident handling
├── events/             # Event handling module
│   ├── ingestion/      # Event intake
│   ├── routing/        # Agent routing
│   ├── correlation/    # Event correlation
│   └── state_machine/  # Incident state management
├── templates/          # Runtime templates
│   ├── runbooks/       # Incident runbooks
│   ├── incident/       # Incident docs
│   └── architecture/   # SLO/SLI definitions
├── tools/              # Validation and automation
│   ├── validation/     # Configuration validators
│   └── wizard/         # RLC Setup Wizard
├── docs/               # Documentation
│   ├── EVENT-HANDLING.md
│   └── agent-model-advisory.md
├── .rlc/config/        # RLC configuration
│   ├── gates.yaml
│   ├── agent-models-template.yaml
│   └── mcp-servers-template.yaml
├── CLAUDE-CORE.md      # Core framework instructions
├── CLAUDE-SETUP.md     # Setup guide
├── QUICKSTART.md       # Quick start guide
├── AGENT-INDEX.md      # Agent catalog
├── CONTRIBUTING.md     # Contribution guidelines
└── CHANGELOG.md        # Version history
```

## Requirements

- Python 3.8+ (for setup scripts)
- Git 2.0+
- Ollama or vLLM (for local AI models)
- Kubernetes/Docker (for containerized workloads)

## Contributing

This framework follows the same principles as ai-first-sdlc-practices:
- Team-first agent collaboration
- Zero tolerance for shortcuts
- Comprehensive documentation
- Continuous validation

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## Version

Current version: **0.2.0**

See [CHANGELOG.md](CHANGELOG.md) for version history and changes.

## License

MIT License - See [LICENSE](LICENSE) for details.

## Related Projects

- [ai-first-sdlc-practices](https://github.com/SteveGJones/ai-first-sdlc-practices) - SDLC framework
- [agent-sdk-python](https://github.com/anthropics/agent-sdk-python) - Agent SDK for Python
- [Anthropic MCP](https://github.com/anthropics/mcp-model-context-protocol) - Model Context Protocol

---

**Remember**: Production runtime is where software meets reality. RLC ensures your systems survive that encounter.
