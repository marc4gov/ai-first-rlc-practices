# AI Model Advisory for RLC Agents

**Last Updated**: 2025-02-17

## Overview

This document provides recommendations for AI models to power each RLC agent, with emphasis on open-source and local deployment options. It also covers agent-to-agent communication patterns and MCP (Model Context Protocol) server integration.

## Agent Model Recommendations

### Core Agents

#### Incident Commander

**Task Complexity**: High | **Latency Sensitivity**: Low | **Context Window**: Large

| Tier | Model | Parameters | Why |
|------|-------|------------|-----|
| **Budget** | Llama 3.2 3B | 3B | Fast incident triage, low resource usage |
| **Balanced** | Mistral 7B v0.3 | 7B | Good reasoning, fast response |
| **Premium** | Qwen 2.5 14B | 14B | Excellent incident analysis and decision-making |
| **Local** | Granite 3.0 8B Instruct | 8B | Business-focused, reliable for incident handling |

**Communication Style**: Command and control, needs clear authority
**Recommended Backend**: Ollama, FastChat, or vLLM for local serving

```yaml
incident_commander:
  model:
    primary: "mistral:7b-instruct-v0.3-q4_k_m"
    fallback: "llama3.2:3b-instruct-q4_k_m"
    backend: "ollama"
    temperature: 0.3  # Lower temperature for consistent decisions
    max_tokens: 2048
  capabilities:
    - incident_classification
    - severity_assessment
    - escalation_decisions
    - resource_allocation
```

#### Auto-Remediator

**Task Complexity**: Medium | **Latency Sensitivity**: High | **Context Window**: Medium

| Tier | Model | Parameters | Why |
|------|-------|------------|-----|
| **Budget** | Phi-3.5 3.8B | 3.8B | Fast action selection, Microsoft quality |
| **Balanced** | Llama 3.2 3B Instruct | 3B | Excellent speed/quality tradeoff |
| **Premium** | Mistral 7B v0.3 | 7B | Better reasoning for complex remediation |
| **Specialized** | ToolForge 7B | 7B | Fine-tuned for tool/API calling |

```yaml
auto_remediator:
  model:
    primary: "phi3.5:3.8b-instruct-q4_k_m"
    fallback: "llama3.2:3b-instruct-q4_k_m"
    backend: "ollama"
    temperature: 0.2  # Very low for consistent actions
    max_tokens: 1024
  capabilities:
    - safe_action_selection
    - rollback_decisions
    - remediation_planning
    - safety_verification
```

#### Post-Mortem Writer

**Task Complexity**: High | **Latency Sensitivity**: Low | **Context Window**: Large

| Tier | Model | Parameters | Why |
|------|-------|------------|-----|
| **Budget** | Qwen 2.5 7B Instruct | 7B | Excellent writing, analysis |
| **Balanced** | Command R 7B | 7B | Great at structured output, analysis |
| **Premium** | Mixtral 8x7B Instruct | 46B | Deep analysis, blameless writing expertise |
| **Local** | Gemma 2 9B IT | 9B | Google quality, excellent for documentation |

```yaml
post_mortem_writer:
  model:
    primary: "qwen2.5:7b-instruct-q4_k_m"
    fallback: "command-r:7b-instruct-q4_k_m"
    backend: "ollama"
    temperature: 0.7  # Higher for creative but factual writing
    max_tokens: 4096
  capabilities:
    - root_cause_analysis
    - blameless_documentation
    - action_item_generation
    - timeline_reconstruction
```

### Observer Agents

#### Metrics Collector

**Task Complexity**: Low | **Latency Sensitivity**: Low | **Specialized**: Yes

**Recommendation**: Use lightweight models for metric interpretation, or specialized tools

| Model | Parameters | Why |
|-------|------------|-----|
| **Text** | Phi-3.5 3.8B | Interpret metric anomalies |
| **Primary** | Prometheus/rules | Native alerting (no AI needed) |
| **Analysis** | Granite 3.0 3B | Quick metric summarization |

```yaml
metrics_collector:
  model:
    primary: "phi3.5:3.8b-instruct-q4_k_m"
    backend: "ollama"
    temperature: 0.1
  mode: "hybrid"  # Rules-based + AI interpretation
```

#### Log Aggregator

**Task Complexity**: Medium | **Specialized**: Embedding-based search

**Recommendation**: Use embedding models for log search, small models for summarization

| Component | Model | Purpose |
|-----------|-------|---------|
| **Embeddings** | bge-base-en-v1.5 | Log vectorization |
| **Retrieval** | N/A | Vector DB (FAISS/Qdrant) |
| **Summarization** | Phi-3.5 3.8B | Log pattern summarization |

```yaml
log_aggregator:
  model:
    primary: "phi3.5:3.8b-instruct-q4_k_m"
    embedding_model: "bge-base-en-v1.5"
    backend: "ollama"
  vector_store: "faiss"  # or qdrant, milvus
```

#### Health Checker

**Task Complexity**: Low | **Latency Sensitivity**: High

**Recommendation**: Rule-based with optional AI for status interpretation

| Model | Parameters | Why |
|-------|------------|-----|
| **Optional** | TinyLlama 1.1B | Very fast status interpretation |
| **Primary** | Health checks | HTTP/TCP probes (no AI) |

### Monitor Agents

#### Anomaly Detector

**Task Complexity**: High | **Specialized**: Statistical + ML

**Recommendation**: Use specialized anomaly detection, LLM for explanation only

| Component | Model | Purpose |
|-----------|-------|---------|
| **Detection** | DBSCAN, Isolation Forest | Statistical anomaly detection |
| **Explanation** | Llama 3.2 3B | Explain anomalies in natural language |

```yaml
anomaly_detector:
  model:
    primary: "llama3.2:3b-instruct-q4_k_m"
    backend: "ollama"
  detection:
    primary: "statistical"  # z-score, moving average
    secondary: "isolation_forest"
```

#### Threshold Evaluator

**Task Complexity**: Low | **Latency Sensitivity**: High

**Recommendation**: Rule-based (no AI needed for threshold evaluation)

#### Pattern Recognizer

**Task Complexity**: Medium | **Specialized**: Time-series patterns

| Model | Parameters | Why |
|-------|------------|-----|
| **Pattern** | Prophet, TimesFM | Time-series forecasting |
| **Description** | Phi-3.5 3.8B | Describe patterns in natural language |

### Alerter Agents

#### Alert Router

**Task Complexity**: Medium | **Latency Sensitivity**: High

**Recommendation**: Fast models for quick routing decisions

| Model | Parameters | Why |
|-------|------------|-----|
| **Primary** | Phi-3.5 3.8B | Very fast routing classification |
| **Fallback** | Rule-based | Direct routing for known patterns |

```yaml
alert_router:
  model:
    primary: "phi3.5:3.8b-instruct-q4_k_m"
    backend: "ollama"
    temperature: 0.1
  routing:
    mode: "hybrid"  # AI + rule-based
    fallback_to_rules: true
```

### Controller Agents

#### Auto-Remediator (covered above)

#### Recovery Monitor

**Task Complexity**: Medium | **Latency Sensitivity**: Low

| Model | Parameters | Why |
|-------|------------|-----|
| **Primary** | Llama 3.2 3B | Monitor recovery progress |
| **Fallback** | Phi-3.5 3.8B | Lightweight status checks |

### Responder Agents

#### Runbook Executor

**Task Complexity**: High | **Specialized**: Tool calling

| Model | Parameters | Why |
|-------|------------|-----|
| **Primary** | ToolForge 7B | Fine-tuned for tool use |
| **Alternative** | Mistral 7B v0.3 | Good function calling |
| **Budget** | Llama 3.2 3B | Decent tool support |

```yaml
runbook_executor:
  model:
    primary: "toolforge:7b-instruct-q4_k_m"
    fallback: "mistral:7b-instruct-v0.3-q4_k_m"
    backend: "ollama"
    temperature: 0.2
    tool_calling: true
```

## Open Source Model Backend Options

### Local Serving Backends

| Backend | Resource Usage | Setup Complexity | Best For |
|---------|---------------|------------------|----------|
| **Ollama** | Low | ⭐ Easy | Development, testing |
| **llama.cpp** | Very Low | ⭐⭐ Medium | Resource-constrained |
| **vLLM** | Medium | ⭐⭐⭐ Hard | Production, high throughput |
| **FastChat** | Medium | ⭐⭐ Medium | Multi-model serving |
| **Text Generation Inference (TGI)** | Medium | ⭐⭐⭐ Hard | Enterprise, production |
| **LocalAI** | Low | ⭐ Easy | Drop-in OpenAI replacement |

### Recommended Setup

```bash
# Using Ollama (easiest for development)
ollama pull phi3.5:3.8b-instruct-q4_k_m
ollama pull llama3.2:3b-instruct-q4_k_m
ollama pull mistral:7b-instruct-v0.3-q4_k_m
ollama pull qwen2.5:7b-instruct-q4_k_m

# Using vLLM (for production)
python -m vllm.entrypoints.openai.api_server \
    --model mistralai/Mistral-7B-Instruct-v0.3 \
    --quantization awq \
    --tensor-parallel-size 1
```

## Agent-to-Agent Communication

### Communication Protocols

#### 1. Direct Message Passing

```yaml
communication:
  type: "message_passing"
  protocol: "nats"  # or kafka, rabbitmq, redis
  format: "json"

agents:
  incident_commander:
    subscribes_to:
      - "events.detected"
      - "alerts.critical"
    publishes_to:
      - "incidents.declared"
      - "commands.remediation"

  auto_remediator:
    subscribes_to:
      - "commands.remediation"
    publishes_to:
      - "actions.started"
      - "actions.completed"
```

#### 2. Shared Context with Topic-Based Communication

```yaml
communication:
  type: "topic_based"
  backend: "redis"  # or nats-stream, kafka

topics:
  incidents:
    partitions: 3
    retention: "7d"

  events:
    partitions: 10
    retention: "1d"

  agent_coordination:
    partitions: 1
    retention: "24h"
```

#### 3. Orchestration-Based (Central Coordinator)

```yaml
communication:
  type: "orchestrated"
  orchestrator: "incident_commander"

agents:
  - name: "auto_remediator"
    receives_commands_from: "incident_commander"

  - name: "metrics_collector"
    sends_reports_to: "incident_commander"
```

### Recommended Pattern: Hybrid

```yaml
# For RLC, we recommend a hybrid approach:
# 1. High-volume events (metrics, logs) -> Direct streaming
# 2. Incident coordination -> Orchestrated by Incident Commander
# 3. Agent handoffs -> Message-based with context

communication:
  high_volume:
    protocol: "kafka"  # or redis streams
    topics:
      - "metrics.raw"
      - "logs.raw"
      - "events.all"

  coordination:
    protocol: "nats"  # or redis pub/sub
    topics:
      - "rlc.coordination"
      - "rlc.handoffs"
      - "rlc.status"

  orchestration:
    lead_agent: "incident_commander"
    heartbeat_interval: "30s"
```

### Message Format Standards

```json
{
  "message_id": "uuid-v4",
  "from_agent": "metrics_collector",
  "to_agent": "incident_commander",
  "type": "incident.declaration",
  "timestamp": "2025-02-17T10:00:00Z",
  "priority": "SEV0",
  "payload": {
    "summary": "System outage detected",
    "affected_services": ["api", "database"],
    "metrics": {
      "error_rate": 0.95,
      "latency_p99": "30s"
    },
    "suggested_actions": ["declare_incident", "escalate_to_sev0"]
  },
  "context": {
    "incident_id": "INC-2025-001",
    "correlation_id": "trace-12345",
    "previous_messages": ["msg-001", "msg-002"]
  }
}
```

## MCP Server Integration

### What is MCP?

The Model Context Protocol (MCP) enables AI models to interact with external tools, data sources, and other agents through a standardized interface.

### MCP Servers for RLC Agents

#### Recommended MCP Servers

| MCP Server | Purpose | Agent Usage |
|------------|---------|-------------|
| **mcp-server-filesystem** | Read/write files | Post-mortem writer, Config management |
| **mcp-server-postgres** | Database access | Log analysis, Metric queries |
| **mcp-server-prompt** | Prompt templates | All agents for consistent behavior |
| **mcp-server-fetch** | HTTP requests | External API calls, Health checks |
| **mcp-server-kubernetes** | K8s control | Auto-remediator (Pod restart, scale) |
| **mcp-server-sqlite** | Local database | Local state management |

#### Agent-Specific MCP Configurations

##### Incident Commander

```yaml
incident_commander:
  mcp_servers:
    - name: "filesystem"
      enabled: true
      config:
        allowed_paths: ["/var/rlc/incidents", "/var/rlc/runbooks"]

    - name: "postgres"  # For incident database
      enabled: true
      config:
        connection_string: "${DATABASE_URL}"

    - name: "prompt"
      enabled: true
      config:
        templates_path: "/etc/rlc/prompts/incident_commander"
```

##### Auto-Remediator

```yaml
auto_remediator:
  mcp_servers:
    - name: "kubernetes"
      enabled: true
      config:
        kubeconfig: "~/.kube/config"
        allowed_operations:
          - "get_pods"
          - "restart_pod"
          - "scale_deployment"
          - "get_logs"

    - name: "fetch"
      enabled: true
      config:
        allowed_domains: ["*.internal", "api.monitoring.com"]

    - name: "sqlite"
      enabled: true
      config:
        database_path: "/var/rlc/state/actions.db"
```

##### Log Aggregator

```yaml
log_aggregator:
  mcp_servers:
    - name: "postgres"
      enabled: true
      config:
        # Read-only access to logs database
        readonly: true
        connection_string: "${LOGS_DATABASE_URL}"

    - name: "filesystem"
      enabled: true
      config:
        allowed_paths: ["/var/log", "/var/rlc/logs"]
        readonly: true
```

##### Post-Mortem Writer

```yaml
post_mortem_writer:
  mcp_servers:
    - name: "filesystem"
      enabled: true
      config:
        allowed_paths: ["/var/rlc/postmortems"]
        write_allowed: true

    - name: "postgres"
      enabled: true
      config:
        # Read incident data
        connection_string: "${DATABASE_URL}"
        readonly: true

    - name: "prompt"
      enabled: true
      config:
        templates_path: "/etc/rlc/prompts/postmortem"
```

### MCP Server Deployment

#### Local Development

```yaml
# docker-compose.yml for MCP servers
services:
  mcp-bridge:
    image: "modelcontextprotocol/servers:latest"
    ports:
      - "3000:3000"
    environment:
      - MCP_SERVERS=filesystem,postgres,fetch
      - POSTGRES_URL=postgres://user:pass@db:5432/rlc
    volumes:
      - "./data:/var/rlc"
```

#### Production MCP Architecture

```
                    ┌─────────────────┐
                    │  Agent Manager  │
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
         ┌────▼────┐   ┌────▼────┐   ┌────▼────┐
         │   MCP   │   │   MCP   │   │   MCP   │
         │ Server  │   │ Server  │   │ Server  │
         │  (FS)   │   │ (K8s)   │   │ (DB)    │
         └────┬────┘   └────┬────┘   └────┬────┘
              │              │              │
         ┌────▼────┐   ┌────▼────┐   ┌────▼────┐
         │ Files   │   │K8s API  │   │Database │
         └─────────┘   └─────────┘   └─────────┘
```

### MCP Communication with Agent Models

```python
# Example: Auto-remediator using MCP to restart a pod

class AutoRemediatorAgent:
    def __init__(self):
        self.model = Ollama(model="phi3.5:3.8b-instruct-q4_k_m")
        self.mcp_client = MCPClient()

    async def restart_pod(self, pod_name: str, namespace: str):
        # 1. Get current pod status via MCP
        pod_status = await self.mcp_client.call(
            server="kubernetes",
            method="get_pod",
            params={"name": pod_name, "namespace": namespace}
        )

        # 2. Use LLM to verify safe action
        prompt = f"""
        Pod Status: {pod_status}

        Is it safe to restart this pod?
        Consider:
        - Current pod state
        - Recent restarts
        - Service impact

        Respond with SAFE or UNSAFE and reasoning.
        """

        decision = await self.model.generate(prompt, temperature=0.1)

        if "SAFE" in decision:
            # 3. Execute action via MCP
            result = await self.mcp_client.call(
                server="kubernetes",
                method="delete_pod",
                params={"name": pod_name, "namespace": namespace}
            )
            return {"status": "restarted", "result": result}
        else:
            return {"status": "declined", "reason": decision}
```

## Resource Planning

### Compute Requirements per Agent

| Agent | Model | VRAM | CPU | RAM | Notes |
|-------|-------|-----|-----|-----|-------|
| Incident Commander | Mistral 7B | 6GB | 4 cores | 8GB | Can share with other agents |
| Auto-Remediator | Phi-3.5 3.8B | 3GB | 2 cores | 4GB | Needs low latency |
| Post-Mortem Writer | Qwen 7B | 6GB | 4 cores | 8GB | Batch processing OK |
| Metrics Collector | Phi-3.5 3.8B | 3GB | 2 cores | 4GB | Share instance |
| Log Aggregator | Embedding model | 2GB | 2 cores | 4GB | + Vector DB |
| Alert Router | Phi-3.5 3.8B | 3GB | 2 cores | 4GB | Very fast response needed |

### Consolidated Deployment Options

#### Option 1: Single Strong Server
```
- 1x Server with 64GB RAM, 8x GPU (each 24GB)
- Run vLLM with multiple models
- Serve all agents from single instance
```

#### Option 2: Distributed (Recommended for Production)
```
- Incident Commander: Dedicated (7B model)
- Critical Path: 2x servers with 3B models each
- Background Agents: Shared 7B model
- Total: 3-4 servers
```

#### Option 3: Cloud + Hybrid
```
- Local: Fast models (Phi, Llama 3B) for critical agents
- Cloud: Larger models (Mixtral, Qwen 14B) for analysis agents
- MCP Bridge: Connect local and cloud
```

## Prompt Engineering Guidelines

### System Prompts per Agent

#### Incident Commander

```
You are the Incident Commander for a production system.

Your responsibilities:
1. Assess incident severity (SEV0-SEV4)
2. Decide on escalation
3. Allocate resources
4. Coordinate response efforts

Communication style:
- Clear, authoritative
- Brief but informative
- Action-oriented

Always include:
- Current severity assessment
- Recommended immediate actions
- Resource requirements
```

#### Auto-Remediator

```
You are the Auto-Remediator agent.

Safety First Rules:
1. Never take destructive actions without confirmation if severity >= SEV2
2. Prefer reversible actions
3. Always verify action success
4. Rollback automatically if metrics worsen

Available actions:
- restart_pod
- clear_cache
- scale_up
- rollback_deployment (requires approval)

Response format:
- Action to take
- Safety verification
- Rollback plan
```

## Summary

| Agent | Recommended Model | Backend | MCP Servers |
|-------|------------------|---------|-------------|
| Incident Commander | Mistral 7B v0.3 | Ollama/vLLM | filesystem, postgres, prompt |
| Auto-Remediator | Phi-3.5 3.8B | Ollama | kubernetes, fetch, sqlite |
| Post-Mortem Writer | Qwen 2.5 7B | Ollama/vLLM | filesystem, postgres, prompt |
| Metrics Collector | Phi-3.5 3.8B | Ollama | postgres |
| Log Aggregator | Phi-3.5 3.8B + bge-base | Ollama | postgres, filesystem |
| Health Checker | Rules (no AI) | - | fetch |
| Anomaly Detector | Llama 3.2 3B (explain) | Ollama | postgres |
| Alert Router | Phi-3.5 3.8B | Ollama | - |
| Runbook Executor | ToolForge 7B / Mistral 7B | Ollama | kubernetes, fetch |
| Recovery Monitor | Llama 3.2 3B | Ollama | postgres |
