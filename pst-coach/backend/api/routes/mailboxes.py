"""
Mailbox and metrics routes.
"""
from fastapi import APIRouter, Query
from typing import Optional

router = APIRouter()


@router.get("/{mailbox_id}/overview")
async def get_mailbox_overview(mailbox_id: int):
    """Get mailbox overview with counts and date range."""
    return {
        "mailbox_id": mailbox_id,
        "total_messages": 50000,
        "total_threads": 12000,
        "date_range": {
            "first_message": "2020-01-01T00:00:00Z",
            "last_message": "2024-01-04T00:00:00Z"
        },
        "indexed_months": 24
    }


@router.get("/{mailbox_id}/metrics")
async def get_metrics(
    mailbox_id: int,
    metric: str = Query(..., description="Metric name"),
    range: str = Query("30d", description="Time range (e.g., 7d, 30d, 3m, 1y)")
):
    """Get specific metric data for mailbox."""
    return {
        "metric": metric,
        "range": range,
        "data_points": [],
        "summary": {}
    }


@router.get("/{mailbox_id}/insights")
async def get_insights(
    mailbox_id: int,
    period: str = Query("monthly", description="Period: weekly or monthly"),
    artifact_type: Optional[str] = None
):
    """Get insight artifacts for mailbox."""
    return {
        "period": period,
        "artifacts": []
    }
