# RLC Quick Start

## For Users: How to Get Claude to Set Up RLC for Your Runtime

### Step 1: Open your infrastructure repository

Navigate to your infrastructure or deployment repository where you want to implement RLC practices.

### Step 2: Give Claude this prompt

```
I want to set up the AI-First RLC framework from https://github.com/your-org/ai-first-rlc-practices for my production runtime.
```

Claude will ask you:
```
What type of workload are you running?
1. Web application
2. API/Backend service
3. Frontend/Static site
4. Microservices
5. Background workers
```

You can respond with your workload type and optionally specify:
- Cloud provider (AWS, GCP, Azure, Hetzner, etc.)
- Platform (Kubernetes, serverless, PaaS, VM)
- Tier preference (budget, balanced, premium)

### Step 3: What Claude will do

1. **Analyze** your codebase for languages, frameworks, deployment configs
2. **Ask** about hosting preferences (if unclear from code)
3. **Prescribe** event handling stack and agent team configuration
4. **Generate** setup artifacts in `./rlc-setup/`
5. **Run** the Construction Agent to build infrastructure
6. **Configure** AI models and MCP servers for each agent

### Step 4: When Claude needs your help

Claude may ask you to:
- **Select hosting**: Choose your cloud provider or "unknown"
- **Choose tier**: Budget (self-hosted), Balanced (managed), or Premium (enterprise)
- **Confirm models**: Review recommended AI models for your tier

### Step 5: Verify setup

After setup, Claude will show you:
- ✅ Event handling configuration
- ✅ Agent team composition
- ✅ AI model requirements
- ✅ MCP server connections
- 📋 Next steps for deployment

## Example Complete Interaction

**You:**
```
I want to set up the AI-First RLC framework for my FastAPI service running on Kubernetes.
```

**Claude:**
```
I'll set up RLC for your FastAPI service on Kubernetes...

Analyzing your codebase...
Languages: python
Frameworks: fastapi
Deployment: kubernetes
Cloud Provider: unknown
```

**Claude (asks):**
```
Which cloud provider hosts your Kubernetes cluster?
1. AWS (EKS)
2. GCP (GKE)
3. Azure (AKS)
4. Self-hosted
5. European provider (Hetzner, Scaleway, OVHcloud)
```

**You:**
```
We're on AWS EKS.
```

**Claude:**
```
Great! For AWS EKS, I recommend the Balanced tier with Grafana Cloud for observability.
This gives you managed metrics/logs/traces with excellent EU support.

[Runs wizard and construction agent]

✅ Setup complete!

Your RLC configuration:
- Event Handling: Grafana Cloud (Balanced tier)
- Incident Commander: Mistral 7B
- Auto-Remediator: Phi-3.5 3.8B
- ...

Next steps:
1. ./rlc-setup/install-agents.sh
2. ollama pull mistral:7b-instruct-v0.3-q4_k_m
3. ./rlc/scripts/setup-models.sh
```

## What You Get

After setup, your infrastructure repo will have:

- 📄 `.rlc/config/gates.yaml` - RLC gates configuration
- 📄 `.rlc/config/agent-models.yaml` - AI model per agent
- 📄 `.rlc/config/mcp-servers.yaml` - MCP server connections
- 📄 `.rlc/agents/*.yaml` - Individual agent configurations
- 📄 `.rlc/scripts/` - Setup and validation scripts
- 📄 `observability/` - Event handling infrastructure configs
- 📄 `docker-compose.obs.yml` - Local observability stack (budget tier)

## Running RLC Agents

Once configured, start your RLC agents:

```bash
# Start Ollama (model backend)
ollama serve &

# Start MCP bridge (tool access)
mcp-bridge --config .rlc/config/mcp-servers.yaml &

# Start incident commander agent
python -m rlc.agents.incident_commander --config .rlc/agents/incident-commander.yaml

# Start other agents as needed
python -m rlc.agents.auto_remediator --config .rlc/agents/auto-remediator.yaml
```

## Tier Comparison

| Tier | VRAM | RAM | Models | Monthly Cost | Best For |
|------|------|-----|--------|-------------|----------|
| **Budget** | 8GB | 16GB | 2 (~5GB) | <$50 | Dev, resource-constrained |
| **Balanced** | 16GB | 32GB | 4 (~15GB) | $50-150 | Production |
| **Premium** | 32GB | 64GB | 4 (~42GB) | $200-1000+ | Enterprise |

## Next Steps

1. Configure your observability credentials (Grafana Cloud, Datadog, etc.)
2. Start the model backend (Ollama or vLLM)
3. Run the model setup script to download models
4. Start MCP servers for tool access
5. Deploy your first RLC agent and test!
