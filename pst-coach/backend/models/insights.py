"""
Insights and metrics models.
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, JSON, Enum
from sqlalchemy.orm import relationship
import enum

from models.base import TimeStampedModel


class MetricName(str, enum.Enum):
    """Metric name types."""
    VOLUME = "volume"
    AFTER_HOURS = "after_hours"
    RESPONSE_LATENCY = "response_latency"
    INITIATION_RATIO = "initiation_ratio"
    THREAD_DEPTH = "thread_depth"
    URGENCY_TREND = "urgency_trend"
    TONE_SENTIMENT = "tone_sentiment"


class ArtifactType(str, enum.Enum):
    """Insight artifact types."""
    THEMES = "themes"
    WORKLOAD = "workload"
    COACHING = "coaching"
    TONE = "tone"
    WEEKLY_PLAN = "weekly_plan"


class MetricsTimeseries(TimeStampedModel):
    """Time-series metrics storage."""

    __tablename__ = "metrics_timeseries"

    tenant_id = Column(Integer, nullable=False, index=True)
    mailbox_id = Column(Integer, ForeignKey("mailboxes.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_name = Column(Enum(MetricName), nullable=False, index=True)
    bucket_start = Column(DateTime, nullable=False, index=True)
    bucket_end = Column(DateTime, nullable=False)
    value_json = Column(JSON, nullable=False)


class InsightArtifact(TimeStampedModel):
    """Generated insight artifacts."""

    __tablename__ = "insight_artifacts"

    tenant_id = Column(Integer, nullable=False, index=True)
    mailbox_id = Column(Integer, ForeignKey("mailboxes.id", ondelete="CASCADE"), nullable=False, index=True)
    period_start = Column(DateTime, nullable=False, index=True)
    period_end = Column(DateTime, nullable=False)
    artifact_type = Column(Enum(ArtifactType), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    summary_text = Column(Text, nullable=False)
    evidence_refs_json = Column(JSON, default={})
    confidence = Column(String(20), default="medium")

    # Vector index reference
    vector_id = Column(String(255), index=True)
