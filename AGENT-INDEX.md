# RLC Agent Catalog Index

*Generated: 2025-02-17*
*Total Agents: 10*

## Agents by Category

### Core (3 agents)

#### `incident-commander`
- **Path**: `agents/core/incident-commander.md`
- **Description**: Orchestrates incident response, assigns severity, coordinates team handoffs
- **Keywords**: incident, response, coordination, severity, escalation
- **AI Model**: Mistral 7B (balanced), Qwen 2.5 14B (premium)
- **MCP Servers**: filesystem, postgres, prompt

#### `auto-remediator`
- **Path**: `agents/core/auto-remediator.md`
- **Description**: Executes safe automated remediation actions with approval gates
- **Keywords**: remediation, automation, recovery, rollback, scale
- **AI Model**: Phi-3.5 3.8B (budget/balanced), Mistral 7B (premium)
- **MCP Servers**: kubernetes, fetch, sqlite

#### `post-mortem-writer`
- **Path**: `agents/core/post-mortem-writer.md`
- **Description**: Creates blameless post-mortem documentation with root cause analysis
- **Keywords**: incident, postmortem, blameless, root-cause, documentation
- **AI Model**: Phi-3.5 3.8B (budget), Qwen 2.5 7B (balanced), Mixtral 8x7B (premium)
- **MCP Servers**: filesystem, postgres, prompt

### Observers (3 agents)

#### `metrics-collector`
- **Path**: `agents/observers/metrics-collector.md`
- **Description**: Gathers Prometheus metrics, computes RED method scores
- **Keywords**: metrics, prometheus, red-method, otel, collection
- **AI Model**: Phi-3.5 3.8B
- **MCP Servers**: postgres

#### `log-aggregator`
- **Path**: `agents/observers/log-aggregator.md`
- **Description**: Centralizes logs with vector embedding for semantic search
- **Keywords**: logs, loki, aggregation, search, embeddings
- **AI Model**: Phi-3.5 3.8B
- **Embedding**: bge-base-en-v1.5
- **MCP Servers**: postgres, filesystem

#### `health-checker`
- **Path**: `agents/core/health-checker.md` (to be created)
- **Description**: Monitors service health endpoints, tracks availability
- **Keywords**: health, uptime, http, tcp, probes
- **AI Model**: Rule-based (no AI needed)
- **MCP Servers**: fetch

### Monitors (3 agents)

#### `anomaly-detector`
- **Path**: `agents/monitors/anomaly-detector.md`
- **Description**: Identifies unusual patterns in metrics and logs
- **Keywords**: anomaly, detection, outliers, statistical, ml
- **AI Model**: Llama 3.2 3B (budget/balanced), Mistral 7B (premium)
- **MCP Servers**: postgres

#### `threshold-evaluator`
- **Path**: `agents/monitors/threshold-evaluator.md` (to be created)
- **Description**: Evaluates metrics against SLO thresholds
- **Keywords**: threshold, slo, evaluation, alerting
- **AI Model**: Rule-based (no AI needed)

#### `pattern-recognizer`
- **Path**: `agents/monitors/pattern-recognizer.md` (to be created)
- **Description**: Recognizes temporal patterns in metrics and logs
- **Keywords**: pattern, time-series, forecasting, prophet
- **AI Model**: Phi-3.5 3.8B

### Alerters (1 agent)

#### `alert-router`
- **Path**: `agents/core/alert-router.md` (to be created)
- **Description**: Routes alerts to appropriate responders based on classification
- **Keywords**: alert, routing, classification, escalation
- **AI Model**: Phi-3.5 3.8B (fast routing decisions)
- **MCP Servers**: (none - fast path)

### Responders (2 agents)

#### `runbook-executor`
- **Path**: `agents/core/runbook-executor.md` (to be created)
- **Description**: Executes runbook procedures with tool calling
- **Keywords**: runbook, execution, tools, kubernetes, api
- **AI Model**: Llama 3.2 3B (budget), Mistral 7B (balanced), Qwen 2.5 14B (premium)
- **MCP Servers**: kubernetes, fetch

#### `recovery-monitor`
- **Path**: `agents/core/recovery-monitor.md` (to be created)
- **Description**: Monitors recovery progress after remediation
- **Keywords**: recovery, monitoring, verification, rollback
- **AI Model**: Llama 3.2 3B
- **MCP Servers**: postgres

## Agent Collaboration

The "Emergency Response 3-2-3-2" formation:

```
┌──────────────────────────────────────────────────────────────┐
│                    Incident Commander (3)                     │
│  - Coordinates all response                                 │
│  - Makes escalation decisions                                │
│  - Assigns ownership                                       │
└──────────────────────────┬───────────────────────────────────┘
                           │
        ┌──────────────────┴────────────────────────┐
        ▼                                         ▼
┌───────────────┐                         ┌───────────────┐
│   Observers   │                         │  Controllers  │
│   (2)          │                         │   (2)          │
│ Metrics       │                         │ Auto          │
│ Logs          │                         │ Remediator    │
└───────────────┘                         └───────────────┘
        │                                         │
        └──────────────────┬────────────────────────┘
                           ▼
                  ┌─────────────────┴──────────────────┐
                  │        Responders (3)          │
                  │  Runbook Executor            │
                  │  Recovery Monitor            │
                  │  Post-Mortem Writer          │
                  └──────────────────────────────┘
```

## Communication Channels

- **`rlc.coordination`** - Agent handoffs and status updates
- **`rlc.handoffs`** - Transfer of incident ownership
- **`rlc.status`** - Broadcasts about system state
- **`incident_response`** - Incident-specific channel

## Model Recommendations Summary

| Tier | Core Agents | Observer Agents | Responder Agents |
|------|-------------|-----------------|------------------|
| Budget | 3-4B | 3-4B | 3-4B |
| Balanced | 7B | 3-4B | 3-7B |
| Premium | 14B+ | 3-7B | 3-14B |

See [docs/agent-model-advisory.md](docs/agent-model-advisory.md) for detailed model recommendations.
