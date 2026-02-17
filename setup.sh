#!/bin/bash
# AI-First RLC Setup Script
# This script sets up the Runtime LifeCycle framework

set -e

echo "🚀 Setting up AI-First Runtime LifeCycle Framework..."

# Detect Python
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Python not found. Please install Python 3.9+ first."
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
echo "✅ Found Python $PYTHON_VERSION"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    $PYTHON_CMD -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
if [ -f "requirements.txt" ]; then
    echo "📥 Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
fi

# Create bin directory
mkdir -p bin

# Create helper scripts
echo "📝 Creating helper scripts..."

# Claude launcher
cat > bin/claude << 'EOF'
#!/bin/bash
# RLC Claude Launcher

# Activate virtual environment
cd "$(dirname "$0")/.."
source venv/bin/activate

# Launch Claude with RLC context
echo "🚀 Launching Claude with RLC context..."
claude .
EOF

chmod +x bin/claude

# Events CLI
cat > bin/events << 'EOF'
#!/usr/bin/env python3
"""
RLC Events CLI
Unified interface for event management
"""
import sys
import os

# Add events to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'events'))

from ingestion.event_ingester import EventIngester
from routing.event_router import create_default_router
from state_machine.incident_state_machine import IncidentStateMachine

if __name__ == "__main__":
    print("RLC Events CLI")
    print("Use: python events/ingestion/event-ingester.py --help")
    print("Use: python events/routing/event-router.py --help")
    print("Use: python events/state_machine/incident-state-machine.py --help")
EOF

chmod +x bin/events

# Incident CLI
cat > bin/incident << 'EOF'
#!/usr/bin/env python3
"""
RLC Incident CLI
Unified interface for incident management
"""
import sys
import os

# Add events to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'events'))

from state_machine.incident_state_machine import main

if __name__ == "__main__":
    main()
EOF

chmod +x bin/incident

# Copy agent configuration
echo "📋 Setting up agent configuration..."
mkdir -p ~/.rlc/config
cp .rlc/config/rlc-gates.yaml ~/.rlc/config/ 2>/dev/null || echo "Config already exists"

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Activate venv: source venv/bin/activate"
echo "  2. Launch Claude: ./bin/claude"
echo "  3. Or use CLI tools:"
echo "     - ./bin/events --help"
echo "     - ./bin/incident --help"
echo ""
echo "For more information, see CLAUDE-SETUP.md"
