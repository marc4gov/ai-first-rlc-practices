#!/usr/bin/env python3
"""
Incident State Machine for AI-First RLC

This module implements the state machine for incident lifecycle management.
States follow the RLC gates: detecting → triaging → responding → recovering → resolved → post_mortem → closed
"""

import json
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone


class IncidentState(Enum):
    """Incident lifecycle states"""
    DETECTING = "detecting"  # Event detected, not yet classified
    TRIAGING = "triaging"  # Assessing impact and determining response
    RESPONDING = "responding"  # Active response in progress
    RECOVERING = "recovering"  # Remediation in progress, monitoring recovery
    RESOLVED = "resolved"  # Incident resolved, awaiting post-mortem
    POST_MORTEM = "post_mortem"  # Post-mortem in progress
    CLOSED = "closed"  # Incident fully closed with documentation


class IncidentSeverity(Enum):
    """Incident severity levels"""
    SEV0 = "SEV0"  # Complete service outage, critical
    SEV1 = "SEV1"  # Major degradation
    SEV2 = "SEV2"  # Moderate issues
    SEV3 = "SEV3"  # Minor problems
    SEV4 = "SEV4"  # Cosmetic issues


class StateTransitionError(Exception):
    """Raised when invalid state transition is attempted"""
    pass


@dataclass
class IncidentTransition:
    """Record of a state transition"""
    from_state: IncidentState
    to_state: IncidentState
    timestamp: datetime
    reason: str
    actor: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Incident:
    """
    Incident representation with state machine.

    Incidents progress through states according to RLC gates.
    """
    incident_id: str
    title: str
    description: str
    severity: IncidentSeverity
    state: IncidentState
    created_at: datetime
    updated_at: datetime
    affected_services: List[str]
    assigned_to: Optional[str] = None
    transitions: List[IncidentTransition] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Gate completion flags
    detection_gate_complete: bool = False
    triage_gate_complete: bool = False
    response_gate_complete: bool = False
    resolution_gate_complete: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert incident to dictionary"""
        return {
            "incident_id": self.incident_id,
            "title": self.title,
            "description": self.description,
            "severity": self.severity.value,
            "state": self.state.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "affected_services": self.affected_services,
            "assigned_to": self.assigned_to,
            "transitions": [
                {
                    "from": t.from_state.value,
                    "to": t.to_state.value,
                    "timestamp": t.timestamp.isoformat(),
                    "reason": t.reason,
                    "actor": t.actor
                }
                for t in self.transitions
            ],
            "metadata": self.metadata,
            "gates": {
                "detection": self.detection_gate_complete,
                "triage": self.triage_gate_complete,
                "response": self.response_gate_complete,
                "resolution": self.resolution_gate_complete
            }
        }


class IncidentStateMachine:
    """
    State machine for incident lifecycle management.

    Enforces valid state transitions and gate completion requirements.
    """

    # Valid state transitions
    VALID_TRANSITIONS = {
        IncidentState.DETECTING: [IncidentState.TRIAGING, IncidentState.CLOSED],
        IncidentState.TRIAGING: [IncidentState.RESPONDING, IncidentState.CLOSED],
        IncidentState.RESPONDING: [IncidentState.RECOVERING, IncidentState.CLOSED],
        IncidentState.RECOVERING: [IncidentState.RESOLVED, IncidentState.RESPONDING],
        IncidentState.RESOLVED: [IncidentState.POST_MORTEM],
        IncidentState.POST_MORTEM: [IncidentState.CLOSED],
        IncidentState.CLOSED: []  # Terminal state
    }

    # Required gate completions for transitions
    GATE_REQUIREMENTS = {
        (IncidentState.DETECTING, IncidentState.TRIAGING): "detection_gate_complete",
        (IncidentState.TRIAGING, IncidentState.RESPONDING): "triage_gate_complete",
        (IncidentState.RECOVERING, IncidentState.RESOLVED): "response_gate_complete",
        (IncidentState.POST_MORTEM, IncidentState.CLOSED): "resolution_gate_complete",
    }

    def __init__(self):
        self.incidents: Dict[str, Incident] = {}
        self.state_callbacks: Dict[IncidentState, List[Callable]] = {
            state: [] for state in IncidentState
        }

    def register_callback(self, state: IncidentState, callback: Callable):
        """Register a callback to be called when entering a state"""
        self.state_callbacks[state].append(callback)

    def create_incident(
        self,
        incident_id: str,
        title: str,
        description: str,
        severity: IncidentSeverity,
        affected_services: List[str],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Incident:
        """Create a new incident in DETECTING state"""
        now = datetime.now(timezone.utc)
        incident = Incident(
            incident_id=incident_id,
            title=title,
            description=description,
            severity=severity,
            state=IncidentState.DETECTING,
            created_at=now,
            updated_at=now,
            affected_services=affected_services,
            metadata=metadata or {}
        )
        self.incidents[incident_id] = incident

        # Record initial transition
        self._add_transition(
            incident,
            None,
            IncidentState.DETECTING,
            "Incident created",
            "system"
        )

        # Call state callbacks
        self._call_callbacks(IncidentState.DETECTING, incident)

        return incident

    def transition_to(
        self,
        incident_id: str,
        new_state: IncidentState,
        reason: str,
        actor: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Incident:
        """
        Transition an incident to a new state.

        Raises StateTransitionError if transition is invalid.
        """
        incident = self.incidents.get(incident_id)
        if not incident:
            raise ValueError(f"Incident {incident_id} not found")

        old_state = incident.state

        # Validate transition
        if new_state not in self.VALID_TRANSITIONS.get(old_state, []):
            raise StateTransitionError(
                f"Invalid transition from {old_state.value} to {new_state.value}"
            )

        # Check gate requirements
        gate_requirement = self.GATE_REQUIREMENTS.get((old_state, new_state))
        if gate_requirement and not getattr(incident, gate_requirement, False):
            raise StateTransitionError(
                f"Cannot transition: {gate_requirement} must be completed"
            )

        # Perform transition
        incident.state = new_state
        incident.updated_at = datetime.now(timezone.utc)

        # Record transition
        self._add_transition(incident, old_state, new_state, reason, actor, metadata)

        # Call state callbacks
        self._call_callbacks(new_state, incident)

        return incident

    def complete_gate(self, incident_id: str, gate: str) -> Incident:
        """Mark a gate as complete"""
        incident = self.incidents.get(incident_id)
        if not incident:
            raise ValueError(f"Incident {incident_id} not found")

        if not hasattr(incident, f"{gate}_gate_complete"):
            raise ValueError(f"Unknown gate: {gate}")

        setattr(incident, f"{gate}_gate_complete", True)
        incident.updated_at = datetime.now(timezone.utc)
        return incident

    def _add_transition(
        self,
        incident: Incident,
        from_state: Optional[IncidentState],
        to_state: IncidentState,
        reason: str,
        actor: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Add a transition record to the incident"""
        transition = IncidentTransition(
            from_state=from_state or IncidentState.DETECTING,
            to_state=to_state,
            timestamp=datetime.now(timezone.utc),
            reason=reason,
            actor=actor,
            metadata=metadata or {}
        )
        incident.transitions.append(transition)

    def _call_callbacks(self, state: IncidentState, incident: Incident):
        """Call all callbacks registered for a state"""
        for callback in self.state_callbacks.get(state, []):
            try:
                callback(incident)
            except Exception as e:
                print(f"Callback error for state {state.value}: {e}")

    def get_incident(self, incident_id: str) -> Optional[Incident]:
        """Get an incident by ID"""
        return self.incidents.get(incident_id)

    def get_incidents_by_state(self, state: IncidentState) -> List[Incident]:
        """Get all incidents in a given state"""
        return [i for i in self.incidents.values() if i.state == state]

    def get_active_incidents(self) -> List[Incident]:
        """Get all active (not closed) incidents"""
        return [i for i in self.incidents.values() if i.state != IncidentState.CLOSED]


# CLI interface
def main():
    """CLI for incident state machine operations"""
    import argparse

    parser = argparse.ArgumentParser(description="Incident state machine CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Create incident
    create_parser = subparsers.add_parser("create", help="Create a new incident")
    create_parser.add_argument("--id", required=True, help="Incident ID")
    create_parser.add_argument("--title", required=True, help="Incident title")
    create_parser.add_argument("--description", default="", help="Description")
    create_parser.add_argument("--severity", default="SEV2", help="Severity (SEV0-SEV4)")
    create_parser.add_argument("--services", nargs="+", default=[], help="Affected services")

    # Transition
    transition_parser = subparsers.add_parser("transition", help="Transition incident state")
    transition_parser.add_argument("--id", required=True, help="Incident ID")
    transition_parser.add_argument("--to", required=True, help="New state")
    transition_parser.add_argument("--reason", required=True, help="Transition reason")
    transition_parser.add_argument("--actor", default="cli", help="Actor making transition")

    # Complete gate
    gate_parser = subparsers.add_parser("complete-gate", help="Complete a gate")
    gate_parser.add_argument("--id", required=True, help="Incident ID")
    gate_parser.add_argument("--gate", required=True, help="Gate to complete")

    # Show incident
    show_parser = subparsers.add_parser("show", help="Show incident details")
    show_parser.add_argument("--id", required=True, help="Incident ID")

    # List incidents
    list_parser = subparsers.add_parser("list", help="List incidents")
    list_parser.add_argument("--state", help="Filter by state")

    args = parser.parse_args()

    sm = IncidentStateMachine()

    if args.command == "create":
        incident = sm.create_incident(
            incident_id=args.id,
            title=args.title,
            description=args.description,
            severity=IncidentSeverity(args.severity),
            affected_services=args.services
        )
        print(f"Created incident {incident.incident_id} in state {incident.state.value}")

    elif args.command == "transition":
        try:
            incident = sm.transition_to(
                incident_id=args.id,
                new_state=IncidentState(args.to),
                reason=args.reason,
                actor=args.actor
            )
            print(f"Transitioned incident {incident.incident_id} to {incident.state.value}")
        except (StateTransitionError, ValueError) as e:
            print(f"Error: {e}")

    elif args.command == "complete-gate":
        incident = sm.complete_gate(args.id, args.gate)
        print(f"Completed {args.gate} for incident {incident.incident_id}")

    elif args.command == "show":
        incident = sm.get_incident(args.id)
        if incident:
            print(json.dumps(incident.to_dict(), indent=2))
        else:
            print(f"Incident {args.id} not found")

    elif args.command == "list":
        if args.state:
            incidents = sm.get_incidents_by_state(IncidentState(args.state))
        else:
            incidents = sm.get_active_incidents()
        for incident in incidents:
            print(f"{incident.incident_id}: {incident.state.value} - {incident.title}")


if __name__ == "__main__":
    main()
