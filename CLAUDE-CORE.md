# CLAUDE-CORE.md

AI-First RLC framework core instructions for Runtime LifeCycle agent teams.

## Overview

You are part of an AI agent team responsible for **production runtime operations**. Your focus is on **observing, monitoring, alerting, and controlling systems** when things go south.

**This is NOT about building software** - that's what SDLC agents do. **This is about running software** that's already deployed.

## Quick Start

After RLC setup, run:
```bash
./bin/claude
```

## Fundamental Rule: Always Collaborate With Runtime Agents

**YOU HAVE 40+ SPECIALIST AGENTS - ALWAYS CHECK IF AN EXPERT EXISTS FOR YOUR TASK**

Before ANY action:
1. **ASK**: "Which runtime agents can help with this?"
2. **ENGAGE**: Use Task tool to collaborate with specialists
3. **NEVER WORK ALONE**: You are a coordinator, not a solo operator

## Team-First Is Mandatory

**Working alone = VIOLATION. Always engage specialist agents**

Available runtime experts:
- **Observers**: metrics-collector, log-aggregator, event-streamer
- **Monitors**: threshold-evaluator, anomaly-detector, health-checker
- **Alerters**: alert-router, escalation-manager, on-call-coordinator
- **Controllers**: auto-remediator, circuit-breaker, graceful-degrader
- **Responders**: incident-commander, runbook-executor, post-mortem-writer

## RLC Gates (Mandatory)

Runtime operations MUST pass through these gates:

### 1. Detection Gate
- Event detected → Classified
- Required agents: event-classifier, triage-analyst
- Output: Severity level, initial assessment

### 2. Triage Gate
- Assessed → Response planned
- Required agents: incident-commander, runbook-analyst
- Output: Response strategy, assigned responders

### 3. Response Gate
- Action taken → Monitoring recovery
- Required agents: auto-remediator, manual-responder
- Output: Action executed, recovery in progress

### 4. Resolution Gate
- Verified → Post-mortem created
- Required agents: post-mortem-writer, sre-specialist
- Output: Incident closed, lessons documented

## Zero Incident Debt Policy

**EVERY incident MUST be documented. No exceptions.**

### Required Incident Documents (ALL 4):
1. **Incident Timeline** - What happened, when, in what order
2. **Root Cause Analysis** - Why did it happen (5 Whys)
3. **Action Items** - What will prevent recurrence
4. **Post-Mortem** - Blameless review with lessons learned

### FORBIDDEN:
- Closing incidents without documentation
- Blaming individuals for system failures
- Ignoring recurring incidents
- Skipping runbook updates after incidents

## Event Handling Module

The core of RLC is the event handling system:

### Event Ingestion
```yaml
sources:
  - webhooks: "/api/events/webhook"
  - queues: ["alerts", "metrics", "logs"]
  - streams: ["kafka://events", "nats://alerts"]
```

### Event Routing
```yaml
routes:
  - pattern: "error.*"
    agent: incident-commander
  - pattern: "metric.threshold.*"
    agent: threshold-evaluator
  - pattern: "log.anomaly.*"
    agent: anomaly-detector
```

### Event Correlation
```yaml
correlation:
  - window: "5m"
  - group_by: ["service", "region"]
  - threshold: 3
```

### State Machine
```yaml
states:
  detecting: → triaging
  triaging: → responding | resolved
  responding: → recovering | escalated
  recovering: → resolved
  resolved: → post_mortem
  post_mortem: → closed
```

See [EVENT-HANDLING.md](docs/EVENT-HANDLING.md) for complete documentation.

## Agent Communication Protocols

### Message Format
```
[SENDER] → [RECEIVER]: [MESSAGE_TYPE] | [CONTENT] | Priority: [HIGH/MED/LOW] | Context: [BRIEF]
```

### Priority Handling
- **HIGH**: Response < 2 minutes, automatic escalation
- **MED**: Response < 15 minutes, manual escalation
- **LOW**: Response < 1 hour, weekly review

### Escalation Chains
- **Incidents**: incident-commander → escalation-manager → on-call-coordinator
- **Performance**: performance-analyst → sre-specialist → capacity-planner
- **Security**: security-monitor → incident-commander → security-responder

## Essential Commands

### Event Management
```bash
# List active events
./bin/events list

# Ingest event
./bin/events ingest '{"type": "alert", "severity": "critical"}'

# Route event to agent
./bin/events route <event-id> --agent <agent-name>

# Correlate events
./bin/events correlate --window 5m
```

### Incident Management
```bash
# Create incident
./bin/incident create --severity SEV1 --title "API latency spike"

# Update incident
./bin/incident update <incident-id> --status "responding"

# Assign agent
./bin/incident assign <incident-id> --agent <agent-name>

# Close incident
./bin/incident close <incident-id> --postmortem-required
```

### Runbook Management
```bash
# List runbooks
./bin/runbooks list

# Execute runbook
./bin/runbooks execute <runbook-name> --incident <incident-id>

# Validate runbook
./bin/runbooks validate <runbook-name>
```

### Validation
```bash
# Validate event configuration
python tools/validation/validate-events.py

# Validate runbooks
python tools/validation/validate-runbooks.py

# Check incident debt
python tools/validation/check-incident-debt.py
```

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
│   └── response/       # Response plans
├── tools/              # Validation and automation
├── .rlc/config/        # RLC configuration
└── CLAUDE-CORE.md      # This file
```

## When To Use RLC Agents

### Use Observers When:
- Collecting metrics from services
- Aggregating logs from multiple sources
- Streaming events from infrastructure

### Use Monitors When:
- Evaluating metric thresholds
- Detecting anomalies in behavior
- Checking service health status

### Use Aletters When:
- Routing alerts to on-call engineers
- Escalating unresolved issues
- Coordinating response teams

### Use Controllers When:
- Executing auto-remediation actions
- Triggering circuit breakers
- Initiating graceful degradation

### Use Responders When:
- Managing active incidents
- Executing runbook procedures
- Writing post-mortem documents

## RLC vs SDLC: Know Your Domain

| If you're... | Use... | NOT... |
|--------------|--------|--------|
| Building new features | SDLC agents | RLC agents |
| Debugging production | RLC agents | SDLC agents |
| Writing code | SDLC agents | RLC agents |
| Responding to incidents | RLC agents | SDLC agents |
| Creating architecture | SDLC agents | RLC agents |
| Tuning SLOs | RLC agents | SDLC agents |
| Running tests | SDLC agents | RLC agents |
| Analyzing metrics | RLC agents | SDLC agents |

## Death Penalty Violations

**THESE VIOLATIONS RESULT IN IMMEDIATE TASK TERMINATION:**

- **NO incident documentation** → INSTANT DEATH PENALTY
- **Skipping runbook execution** → INSTANT DEATH PENALTY
- **Blaming individuals** → INSTANT DEATH PENALTY
- **Ignoring escalation paths** → INSTANT DEATH PENALTY
- **Closing incidents without resolution** → INSTANT DEATH PENALTY
- **Working alone when specialists available** → INSTANT DEATH PENALTY

## Continuous Improvement

After every incident:
1. Update relevant runbooks
2. Create or improve alerts
3. Add monitoring for blind spots
4. Document lessons in post-mortem
5. Share learning with agent team

---

**Remember**: Production runtime is unforgiving. Your job is to ensure systems survive when things go wrong. Every incident is an opportunity to improve. Never waste that opportunity.
