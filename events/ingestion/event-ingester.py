#!/usr/bin/env python3
"""
Event Ingestion Module for AI-First RLC

This module handles ingestion of events from multiple sources:
- Webhooks (HTTP POST)
- Message queues (SQS, Kafka, NATS)
- Log streams (CloudWatch, Loki, Elasticsearch)
- Metrics (Prometheus alerts)

Events are normalized and routed to the event handler for processing.
"""

import json
import hashlib
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum


class EventType(Enum):
    """Standard event types in the RLC framework"""
    METRIC_ANOMALY = "metric.anomaly"
    METRIC_THRESHOLD = "metric.threshold"
    LOG_ERROR = "log.error"
    LOG_ANOMALY = "log.anomaly"
    TRACE_ERROR = "trace.error"
    HEALTH_CHECK_FAILED = "health.failed"
    DEPLOYMENT_FAILED = "deployment.failed"
    SECURITY_EVENT = "security.event"
    CUSTOMER_REPORT = "customer.report"
    MANUAL_REPORT = "manual.report"


class EventSeverity(Enum):
    """Event severity levels"""
    CRITICAL = "critical"  # Immediate action required
    HIGH = "high"  # Action within 15 minutes
    MEDIUM = "medium"  # Action within 1 hour
    LOW = "low"  # Action within 24 hours
    INFO = "info"  # Informational only


class EventSource(Enum):
    """Event source types"""
    WEBHOOK = "webhook"
    PROMETHEUS = "prometheus"
    CLOUDWATCH = "cloudwatch"
    LOKI = "loki"
    ELASTICSEARCH = "elasticsearch"
    KAFKA = "kafka"
    SQS = "sqs"
    NATS = "nats"
    MANUAL = "manual"


@dataclass
class Event:
    """
    Normalized event structure for the RLC framework.

    All events are converted to this structure regardless of source.
    """
    event_id: str
    event_type: EventType
    severity: EventSeverity
    source: EventSource
    timestamp: datetime
    title: str
    description: str
    metadata: Dict[str, Any]
    source_data: Optional[Dict[str, Any]] = None
    correlation_id: Optional[str] = None
    incident_id: Optional[str] = None
    processed: bool = False
    processing_attempts: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary, handling enums and datetime"""
        data = asdict(self)
        data['event_type'] = self.event_type.value
        data['severity'] = self.severity.value
        data['source'] = self.source.value
        data['timestamp'] = self.timestamp.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        """Create event from dictionary"""
        data['event_type'] = EventType(data['event_type'])
        data['severity'] = EventSeverity(data['severity'])
        data['source'] = EventSource(data['source'])
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


def generate_event_id(event_data: Dict[str, Any]) -> str:
    """
    Generate a deterministic event ID from event data.

    Format: EVT-YYYYMMDD-<hash>
    """
    date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    # Hash of key event fields for uniqueness
    hash_input = json.dumps(event_data, sort_keys=True)
    hash_hex = hashlib.sha256(hash_input.encode()).hexdigest()[:12]
    return f"EVT-{date_str}-{hash_hex}"


class EventIngester:
    """
    Main event ingestion class.

    Handles event ingestion from multiple sources and normalizes
    all events to the standard Event structure.
    """

    def __init__(self):
        self.event_handlers = []
        self.event_buffer = []
        self.buffer_size = 1000

    def register_handler(self, handler):
        """Register an event handler callback"""
        self.event_handlers.append(handler)

    async def ingest_webhook(self, data: Dict[str, Any]) -> Event:
        """
        Ingest event from webhook.

        Expected format:
        {
            "type": "metric.anomaly",
            "severity": "critical",
            "title": "High error rate detected",
            "description": "...",
            "metadata": {...}
        }
        """
        event_id = generate_event_id(data)
        event = Event(
            event_id=event_id,
            event_type=EventType(data.get("type", "custom")),
            severity=EventSeverity(data.get("severity", "medium")),
            source=EventSource.WEBHOOK,
            timestamp=datetime.now(timezone.utc),
            title=data.get("title", "Untitled Event"),
            description=data.get("description", ""),
            metadata=data.get("metadata", {}),
            source_data=data
        )
        return await self._process_event(event)

    async def ingest_prometheus_alert(self, alert: Dict[str, Any]) -> Event:
        """
        Ingest event from Prometheus alert.

        Prometheus webhook format:
        {
            "receiver": "...",
            "status": "firing",
            "alerts": [{
                "status": "firing",
                "labels": {...},
                "annotations": {...},
                "startsAt": "...",
                "endsAt": "..."
            }],
            ...
        }
        """
        # Process first alert for simplicity (can process multiple)
        alert_data = alert.get("alerts", [{}])[0]

        # Determine event type from labels
        alert_name = alert_data.get("labels", {}).get("alertname", "")
        if "anomaly" in alert_name.lower():
            event_type = EventType.METRIC_ANOMALY
        elif "threshold" in alert_name.lower():
            event_type = EventType.METRIC_THRESHOLD
        else:
            event_type = EventType.METRIC_THRESHOLD  # Default

        # Map Prometheus status to severity
        status = alert_data.get("status", "firing")
        if status == "firing":
            # Use labels to determine severity
            severity_label = alert_data.get("labels", {}).get("severity", "warning")
            severity_map = {
                "critical": EventSeverity.CRITICAL,
                "warning": EventSeverity.HIGH,
                "info": EventSeverity.INFO
            }
            severity = severity_map.get(severity_label, EventSeverity.MEDIUM)
        else:
            severity = EventSeverity.INFO

        event = Event(
            event_id=generate_event_id(alert_data),
            event_type=event_type,
            severity=severity,
            source=EventSource.PROMETHEUS,
            timestamp=datetime.fromisoformat(
                alert_data.get("startsAt", datetime.now(timezone.utc).isoformat())
                .replace('Z', '+00:00')
            ),
            title=alert_data.get("annotations", {}).get("summary", alert_name),
            description=alert_data.get("annotations", {}).get("description", ""),
            metadata={
                "labels": alert_data.get("labels", {}),
                "value": alert_data.get("annotations", {}).get("value", "")
            },
            source_data=alert
        )
        return await self._process_event(event)

    async def ingest_cloudwatch_alarm(self, alarm: Dict[str, Any]) -> Event:
        """
        Ingest event from CloudWatch Alarm.

        CloudWatch SNS notification format
        """
        alarm_name = alarm.get("AlarmName", "")
        new_state = alarm.get("NewStateValue", "")
        reason = alarm.get("NewStateReason", "")

        # Map alarm state to severity
        state_to_severity = {
            "ALARM": EventSeverity.CRITICAL,
            "INSUFFICIENT_DATA": EventSeverity.MEDIUM,
            "OK": EventSeverity.INFO
        }
        severity = state_to_severity.get(new_state, EventSeverity.LOW)

        # Determine event type
        metric_name = alarm.get("Trigger", {}).get("MetricName", "")
        event_type = EventType.METRIC_THRESHOLD

        event = Event(
            event_id=generate_event_id(alarm),
            event_type=event_type,
            severity=severity,
            source=EventSource.CLOUDWATCH,
            timestamp=datetime.now(timezone.utc),
            title=f"{alarm_name}: {new_state}",
            description=reason,
            metadata={
                "alarm_name": alarm_name,
                "metric": metric_name,
                "namespace": alarm.get("Trigger", {}).get("Namespace", ""),
                "dimensions": alarm.get("Trigger", {}).get("Dimensions", [])
            },
            source_data=alarm
        )
        return await self._process_event(event)

    async def ingest_manual_report(self, report: Dict[str, Any]) -> Event:
        """
        Ingest manually reported event.

        For events reported by humans via CLI, API, or chat.
        """
        event = Event(
            event_id=generate_event_id(report),
            event_type=EventType.MANUAL_REPORT,
            severity=EventSeverity(report.get("severity", "medium")),
            source=EventSource.MANUAL,
            timestamp=datetime.now(timezone.utc),
            title=report.get("title", "Manual Event Report"),
            description=report.get("description", ""),
            metadata={
                "reported_by": report.get("reported_by", "unknown"),
                "impact": report.get("impact", ""),
                "urgency": report.get("urgency", "normal")
            },
            source_data=report
        )
        return await self._process_event(event)

    async def _process_event(self, event: Event) -> Event:
        """
        Process event through registered handlers.

        Handlers can modify the event or take actions based on it.
        """
        # Add to buffer for persistence/analysis
        self.event_buffer.append(event)
        if len(self.event_buffer) > self.buffer_size:
            self.event_buffer.pop(0)

        # Call registered handlers
        for handler in self.event_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                print(f"Handler error: {e}")

        event.processed = True
        return event

    def get_buffered_events(self, limit: Optional[int] = None) -> List[Event]:
        """Get buffered events, optionally limited"""
        if limit:
            return self.event_buffer[-limit:]
        return self.event_buffer.copy()


# CLI interface for manual event ingestion
def main():
    """CLI for ingesting events manually"""
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="Ingest events into RLC")
    parser.add_argument("--type", required=True, help="Event type")
    parser.add_argument("--severity", default="medium", help="Event severity")
    parser.add_argument("--title", required=True, help="Event title")
    parser.add_argument("--description", default="", help="Event description")
    parser.add_argument("--metadata", default="{}", help="Event metadata as JSON")

    args = parser.parse_args()

    ingester = EventIngester()

    event_data = {
        "type": args.type,
        "severity": args.severity,
        "title": args.title,
        "description": args.description,
        "metadata": json.loads(args.metadata)
    }

    event = asyncio.run(ingester.ingest_manual_report(event_data))
    print(f"Event ingested: {event.event_id}")
    print(json.dumps(event.to_dict(), indent=2))


if __name__ == "__main__":
    main()
