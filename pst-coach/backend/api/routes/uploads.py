"""
Upload routes for PST file handling.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from typing import Dict, List
import os
import json
from services.ingest.service import handle_upload, get_upload_status, get_existing_upload_ids
from services.index.service import get_indexed_uploads
from core.config import settings

router = APIRouter()


@router.post("/")
async def upload_pst(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """
    Upload a PST file for processing.
    If the same file was already uploaded, returns the existing upload_id.
    """
    if not file.filename.endswith(('.pst', '.ost')):
        raise HTTPException(status_code=400, detail="Only .pst or .ost files are allowed")
        
    return await handle_upload(file, background_tasks)


@router.get("/")
async def list_uploads():
    """
    List all processed uploads.
    Returns upload IDs and their status.
    """
    upload_ids = get_existing_upload_ids()
    indexed = get_indexed_uploads()
    
    uploads = []
    for upload_id in upload_ids:
        # Get email count from extracted file
        extracted_path = os.path.join(settings.EXTRACTED_DIR, f"{upload_id}.json")
        email_count = 0
        if os.path.exists(extracted_path):
            try:
                with open(extracted_path, "r", encoding="utf-8") as f:
                    emails = json.load(f)
                    email_count = len(emails)
            except:
                pass
        
        # Get vector count if indexed
        vector_count = 0
        indexed_at = None
        if upload_id in indexed:
            vector_count = indexed[upload_id].get("vector_count", 0)
            indexed_at = indexed[upload_id].get("indexed_at")
        
        uploads.append({
            "upload_id": upload_id,
            "email_count": email_count,
            "vector_count": vector_count,
            "indexed_at": indexed_at,
            "status": "indexed" if upload_id in indexed else "extracted"
        })
    
    return {
        "uploads": uploads,
        "total": len(uploads)
    }


@router.get("/stats")
async def get_stats():
    """
    Get overall statistics about indexed data.
    """
    indexed = get_indexed_uploads()
    
    # Calculate totals
    total_vectors = sum(u.get("vector_count", 0) for u in indexed.values())
    
    return {
        "total_vectors": total_vectors,
        "total_uploads": len(indexed),
        "uploads": indexed
    }


@router.get("/{upload_id}")
async def get_single_upload_status(upload_id: str):
    """Get status of a specific upload."""
    status = await get_upload_status(upload_id)
    
    # Add vector count if indexed
    indexed = get_indexed_uploads()
    if upload_id in indexed:
        status["vector_count"] = indexed[upload_id].get("vector_count", 0)
        status["indexed_at"] = indexed[upload_id].get("indexed_at")
        status["is_indexed"] = True
    else:
        status["is_indexed"] = False
    
    return status


@router.delete("/{upload_id}")
async def delete_upload(upload_id: str):
    """
    Delete an upload and its indexed data.
    """
    # Delete extracted JSON
    extracted_path = os.path.join(settings.EXTRACTED_DIR, f"{upload_id}.json")
    if os.path.exists(extracted_path):
        os.remove(extracted_path)
    
    # Delete PST file
    pst_path = os.path.join(settings.UPLOAD_DIR, f"{upload_id}.pst")
    if os.path.exists(pst_path):
        os.remove(pst_path)
    
    # Remove from indexed tracking
    indexed = get_indexed_uploads()
    if upload_id in indexed:
        del indexed[upload_id]
        indexed_file = os.path.join(settings.DATA_DIR, "indexed_uploads.json")
        with open(indexed_file, "w") as f:
            json.dump(indexed, f, indent=2)
    
    # Note: Deleting vectors from Pinecone would require filtering by upload_id
    # For now, we just remove local tracking
    
    return {
        "message": f"Upload {upload_id} deleted",
        "note": "Vectors in Pinecone will be overwritten on next upload of same content"
    }
