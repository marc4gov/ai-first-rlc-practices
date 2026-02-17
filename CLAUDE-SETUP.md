# RLC Setup Guide

This guide helps you set up the AI-First Runtime LifeCycle framework.

## Quick Start

```bash
# Clone the repository
git clone https://github.com/your-org/ai-first-rlc-practices.git
cd ai-first-rlc-practices

# Run setup
./setup.sh

# Launch Claude with RLC context
./bin/claude
```

## Prerequisites

- Python 3.9+
- Claude Code CLI
- Git
- (Optional) Docker for local testing

## Setup Steps

### 1. Framework Installation

The setup script creates:
- Virtual Python environment
- Required dependencies
- Bin directory with helper scripts
- Agent installation

```bash
./setup.sh
```

### 2. Agent Installation

Install RLC agents in your Claude configuration:

```bash
mkdir -p ~/.claude/agents/rlc
cp -r agents/* ~/.claude/agents/rlc/
```

### 3. Event System Setup

Set up the event handling module:

```bash
# Create Python virtual environment for event system
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Test event ingestion
python events/ingestion/event-ingester.py --help
```

### 4. Configuration

Copy and customize configuration:

```bash
# Copy RLC configuration
cp .rlc/config/rlc-gates.yaml ~/.rlc/config/

# Edit for your environment
# Update severity levels, agent assignments, etc.
```

## Verification

Test your setup:

```bash
# Test event ingestion
python events/ingestion/event-ingester.py \
  --type metric.threshold \
  --severity high \
  --title "Test event"

# Test routing
python events/routing/event-router.py --list-rules

# Test state machine
python events/state_machine/incident-state-machine.py list
```

## Integration with SDLC

If you're also using ai-first-sdlc-practices:

1. Install both frameworks
2. Use SDLC for development work
3. Use RLC for runtime operations

## Next Steps

- Read [CLAUDE-CORE.md](CLAUDE-CORE.md) for framework instructions
- Review [EVENT-HANDLING.md](docs/EVENT-HANDLING.md) for event system details
- Explore agent definitions in `agents/`
- Customize templates in `templates/`

## Troubleshooting

### Python Not Found
```bash
# Check Python version
python --version
# or
python3 --version

# Use python3 if python is not available
```

### Agents Not Loading
```bash
# Verify agent installation
ls ~/.claude/agents/rlc/

# Check Claude configuration
cat ~/.claude/settings.json
```

### Event System Errors
```bash
# Check Python environment
which python
pip list

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## Getting Help

- GitHub Issues: https://github.com/your-org/ai-first-rlc-practices/issues
- Documentation: See `docs/` directory
- Community: [Link to community forum]
