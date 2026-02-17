#!/usr/bin/env python3
"""
Event Routing Module for AI-First RLC

This module routes events to appropriate agents based on:
- Event type classification
- Severity level
- Service/component ownership
- Pattern matching rules

Supports both synchronous (immediate) and asynchronous (queued) routing.
"""

import re
import json
from typing import Dict, Any, List, Callable, Optional
from dataclasses import dataclass
from enum import Enum

from event_ingester import Event, EventType, EventSeverity


class RoutingStrategy(Enum):
    """How to route events to agents"""
    SINGLE = "single"  # Route to single best agent
    BROADCAST = "broadcast"  # Send to all matching agents
    SEQUENTIAL = "sequential"  # Try agents in order until one accepts
    PARALLEL = "parallel"  # Send to multiple agents concurrently


@dataclass
class RoutingRule:
    """
    A routing rule determines which agents handle which events.

    Rules are evaluated in priority order (higher priority first).
    """
    name: str
    priority: int  # Higher = evaluated first
    pattern: str  # Regex pattern to match event type/title
    agent: str  # Target agent name
    strategy: RoutingStrategy
    conditions: Dict[str, Any]  # Additional conditions (severity, metadata)
    timeout_seconds: int = 300  # How long to wait for agent response

    def matches(self, event: Event) -> bool:
        """Check if this rule matches the event"""
        # Check pattern match
        if not re.search(self.pattern, event.event_type.value) and \
           not re.search(self.pattern, event.title, re.IGNORECASE):
            return False

        # Check severity condition
        if "severity" in self.conditions:
            required_severity = self.conditions["severity"]
            if isinstance(required_severity, list):
                if event.severity.value not in required_severity:
                    return False
            elif event.severity.value != required_severity:
                return False

        # Check metadata conditions
        for key, value in self.conditions.items():
            if key == "severity":
                continue
            if key not in event.metadata:
                return False
            if isinstance(value, list):
                if event.metadata[key] not in value:
                    return False
            elif event.metadata[key] != value:
                return False

        return True


class EventRouter:
    """
    Main event routing class.

    Evaluates routing rules and dispatches events to appropriate agents.
    """

    def __init__(self):
        self.rules: List[RoutingRule] = []
        self.agent_registry: Dict[str, Callable] = {}
        self.routing_history: List[Dict[str, Any]] = []
        self.default_agent = "event-classifier"

    def add_rule(self, rule: RoutingRule):
        """Add a routing rule"""
        self.rules.append(rule)
        # Sort by priority (highest first)
        self.rules.sort(key=lambda r: r.priority, reverse=True)

    def register_agent(self, name: str, handler: Callable):
        """Register an agent handler"""
        self.agent_registry[name] = handler

    def route(self, event: Event) -> List[str]:
        """
        Route an event to appropriate agents.

        Returns list of agent names that the event was routed to.
        """
        routed_agents = []

        # Find matching rules
        matching_rules = [rule for rule in self.rules if rule.matches(event)]

        if not matching_rules:
            # Route to default agent
            agent = self.default_agent
            self._dispatch_to_agent(event, agent)
            routed_agents.append(agent)
        else:
            # Use highest priority matching rule
            rule = matching_rules[0]

            if rule.strategy == RoutingStrategy.SINGLE:
                self._dispatch_to_agent(event, rule.agent)
                routed_agents.append(rule.agent)

            elif rule.strategy == RoutingStrategy.BROADCAST:
                for agent in self._get_agents_for_broadcast(rule.agent):
                    self._dispatch_to_agent(event, agent)
                    routed_agents.append(agent)

            elif rule.strategy == RoutingStrategy.SEQUENTIAL:
                accepted = False
                for agent in self._get_agents_for_sequential(rule.agent):
                    if self._dispatch_to_agent(event, agent):
                        routed_agents.append(agent)
                        accepted = True
                        break
                if not accepted:
                    # Fallback to default
                    self._dispatch_to_agent(event, self.default_agent)
                    routed_agents.append(self.default_agent)

            elif rule.strategy == RoutingStrategy.PARALLEL:
                for agent in self._get_agents_for_parallel(rule.agent):
                    self._dispatch_to_agent(event, agent)
                    routed_agents.append(agent)

        # Record routing decision
        self._record_routing(event, routed_agents, matching_rules)

        return routed_agents

    def _dispatch_to_agent(self, event: Event, agent_name: str) -> bool:
        """Dispatch event to a specific agent"""
        if agent_name not in self.agent_registry:
            print(f"Warning: Agent {agent_name} not registered")
            return False

        try:
            handler = self.agent_registry[agent_name]
            handler(event)
            return True
        except Exception as e:
            print(f"Error dispatching to {agent_name}: {e}")
            return False

    def _get_agents_for_broadcast(self, base_agent: str) -> List[str]:
        """Get list of agents for broadcast routing"""
        # Could be expanded to support agent groups
        return [base_agent]

    def _get_agents_for_sequential(self, base_agent: str) -> List[str]:
        """Get ordered list of agents for sequential routing"""
        # Could be expanded to support fallback chains
        return [base_agent]

    def _get_agents_for_parallel(self, base_agent: str) -> List[str]:
        """Get list of agents for parallel routing"""
        # Could be expanded to support agent teams
        return [base_agent]

    def _record_routing(self, event: Event, agents: List[str], rules: List[RoutingRule]):
        """Record routing decision for analysis"""
        self.routing_history.append({
            "event_id": event.event_id,
            "event_type": event.event_type.value,
            "routed_to": agents,
            "matching_rule": rules[0].name if rules else "default",
            "timestamp": event.timestamp.isoformat()
        })

    def get_routing_stats(self) -> Dict[str, Any]:
        """Get statistics about routing decisions"""
        if not self.routing_history:
            return {}

        agent_counts = {}
        for record in self.routing_history:
            for agent in record["routed_to"]:
                agent_counts[agent] = agent_counts.get(agent, 0) + 1

        return {
            "total_routed": len(self.routing_history),
            "agent_distribution": agent_counts,
            "most_common": max(agent_counts.items(), key=lambda x: x[1]) if agent_counts else None
        }


# Default routing rules for RLC
def get_default_routing_rules() -> List[RoutingRule]:
    """
    Get default routing rules for the RLC framework.

    These rules implement standard incident response routing:
    - Critical events → incident-commander
    - Security events → security-monitor + incident-commander
    - Anomalies → anomaly-detector
    - Threshold breaches → threshold-evaluator
    - Manual reports → event-classifier
    """
    return [
        # CRITICAL: All critical events go to incident-commander
        RoutingRule(
            name="critical_to_incident_commander",
            priority=100,
            pattern=".*",
            agent="incident-commander",
            strategy=RoutingStrategy.SINGLE,
            conditions={"severity": ["critical"]},
            timeout_seconds=120
        ),

        # SECURITY: Security events get special handling
        RoutingRule(
            name="security_incident",
            priority=90,
            pattern="security|breach|attack|unauthorized",
            agent="security-monitor",
            strategy=RoutingStrategy.PARALLEL,
            conditions={"severity": ["high", "critical"]},
            timeout_seconds=60
        ),

        # ANOMALY: Metric anomalies go to anomaly detector
        RoutingRule(
            name="metric_anomaly",
            priority=80,
            pattern="metric\\.anomaly|anomaly.*detected",
            agent="anomaly-detector",
            strategy=RoutingStrategy.SINGLE,
            conditions={},
            timeout_seconds=300
        ),

        # THRESHOLD: Threshold breaches to evaluator
        RoutingRule(
            name="threshold_breach",
            priority=70,
            pattern="metric\\.threshold|threshold.*breach",
            agent="threshold-evaluator",
            strategy=RoutingStrategy.SINGLE,
            conditions={},
            timeout_seconds=300
        ),

        # HEALTH: Failed health checks
        RoutingRule(
            name="health_check_failed",
            priority=60,
            pattern="health\\.failed|health.*check.*fail",
            agent="health-checker",
            strategy=RoutingStrategy.SINGLE,
            conditions={},
            timeout_seconds=120
        ),

        # DEPLOYMENT: Deployment failures
        RoutingRule(
            name="deployment_failure",
            priority=85,
            pattern="deployment\\.failed|rollback|deploy.*fail",
            agent="auto-remediator",
            strategy=RoutingStrategy.SINGLE,
            conditions={},
            timeout_seconds=60
        ),

        # CUSTOMER: Customer-reported issues
        RoutingRule(
            name="customer_report",
            priority=95,
            pattern="customer\\.report|customer.*complaint",
            agent="incident-commander",
            strategy=RoutingStrategy.SINGLE,
            conditions={},
            timeout_seconds=300
        ),

        # MANUAL: Manual reports need classification
        RoutingRule(
            name="manual_report",
            priority=50,
            pattern="manual\\.report",
            agent="event-classifier",
            strategy=RoutingStrategy.SINGLE,
            conditions={},
            timeout_seconds=300
        ),

        # DEFAULT: Log errors
        RoutingRule(
            name="log_error",
            priority=40,
            pattern="log\\.error|error.*log",
            agent="log-analyzer",
            strategy=RoutingStrategy.SINGLE,
            conditions={},
            timeout_seconds=300
        ),
    ]


def create_default_router() -> EventRouter:
    """Create an EventRouter with default rules"""
    router = EventRouter()
    for rule in get_default_routing_rules():
        router.add_rule(rule)
    return router


# CLI interface
def main():
    """CLI for testing event routing"""
    import argparse
    from event_ingester import EventIngester, Event, EventType, EventSeverity, EventSource
    from datetime import datetime, timezone

    parser = argparse.ArgumentParser(description="Route events to agents")
    parser.add_argument("--event-id", help="Event ID (generates if not provided)")
    parser.add_argument("--type", default="metric.threshold", help="Event type")
    parser.add_argument("--severity", default="high", help="Event severity")
    parser.add_argument("--title", required=True, help="Event title")
    parser.add_argument("--list-rules", action="store_true", help="List routing rules")

    args = parser.parse_args()

    router = create_default_router()

    if args.list_rules:
        print("Routing Rules:")
        for rule in router.rules:
            print(f"  {rule.priority}: {rule.name} -> {rule.agent} ({rule.strategy.value})")
        return

    # Create test event
    event = Event(
        event_id=args.event_id or "TEST-001",
        event_type=EventType(args.type),
        severity=EventSeverity(args.severity),
        source=EventSource.MANUAL,
        timestamp=datetime.now(timezone.utc),
        title=args.title,
        description="Test event",
        metadata={}
    )

    # Route event
    routed = router.route(event)
    print(f"Event routed to: {', '.join(routed)}")


if __name__ == "__main__":
    main()
