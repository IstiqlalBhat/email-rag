"""
Job management routes.
"""
from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.get("/{job_id}")
async def get_job_status(job_id: str):
    """
    Get job status, progress, and current stage.
    No ETA provided per architectural guidelines.
    """
    return {
        "job_id": job_id,
        "type": "parse_pst",
        "status": "running",
        "progress": 45,
        "total": 100,
        "current_stage": "Parsing email messages",
        "started_at": "2024-01-04T00:00:00Z"
    }


@router.post("/{job_id}/cancel")
async def cancel_job(job_id: str):
    """Cancel a running job."""
    return {
        "job_id": job_id,
        "status": "cancelled",
        "message": "Job cancellation requested"
    }


@router.get("/")
async def list_jobs(status: str = None, job_type: str = None):
    """List jobs with optional filtering."""
    return {
        "jobs": [],
        "total": 0
    }
