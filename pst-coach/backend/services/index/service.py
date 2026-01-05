from typing import List, Dict
import json
import os
import hashlib
from loguru import logger
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from pinecone import Pinecone, ServerlessSpec

# Import settings
from core.config import settings

# Track indexed uploads to avoid re-indexing
_indexed_uploads_file = os.path.join(settings.DATA_DIR, "indexed_uploads.json")


def get_indexed_uploads() -> dict:
    """Get dictionary of already indexed uploads with their vector counts."""
    if os.path.exists(_indexed_uploads_file):
        try:
            with open(_indexed_uploads_file, "r") as f:
                return json.load(f)
        except:
            pass
    return {}


def mark_upload_indexed(upload_id: str, vector_count: int):
    """Mark an upload as indexed."""
    indexed = get_indexed_uploads()
    indexed[upload_id] = {
        "vector_count": vector_count,
        "indexed_at": str(__import__('datetime').datetime.now())
    }
    os.makedirs(os.path.dirname(_indexed_uploads_file), exist_ok=True)
    with open(_indexed_uploads_file, "w") as f:
        json.dump(indexed, f, indent=2)


def ensure_pinecone_index():
    """Ensure Pinecone index exists, create if not."""
    try:
        pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        existing_indexes = [idx.name for idx in pc.list_indexes()]
        
        if settings.PINECONE_INDEX_NAME not in existing_indexes:
            logger.info(f"Creating Pinecone index: {settings.PINECONE_INDEX_NAME}")
            pc.create_index(
                name=settings.PINECONE_INDEX_NAME,
                dimension=settings.EMBEDDING_DIMENSION,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )
            logger.info("Pinecone index created successfully")
            # Wait for index to be ready
            import time
            time.sleep(5)
        return True
    except Exception as e:
        logger.error(f"Failed to ensure Pinecone index: {e}")
        return False


def index_messages(upload_id: str, force_reindex: bool = False):
    """
    Main entry point to index messages for a given upload_id.
    Uses email IDs to avoid duplicate indexing.
    """
    logger.info(f"Starting indexing for upload_id: {upload_id}")
    
    # Check if already indexed
    indexed_uploads = get_indexed_uploads()
    if upload_id in indexed_uploads and not force_reindex:
        logger.info(f"Upload {upload_id} already indexed with {indexed_uploads[upload_id]['vector_count']} vectors. Skipping.")
        return
    
    # Check if extracted file exists
    input_file = os.path.join(settings.EXTRACTED_DIR, f"{upload_id}.json")
    if not os.path.exists(input_file):
        logger.error(f"Extracted file not found: {input_file}")
        return

    try:
        # Ensure Pinecone index exists
        if not ensure_pinecone_index():
            logger.error("Cannot index: Pinecone index not available")
            return
        
        # Load data
        with open(input_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        # Ensure list of dicts
        if isinstance(data, dict):
            data = [data]
            
        logger.info(f"Loaded {len(data)} emails to index")

        # Prepare documents
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP
        )

        # Initialize Embeddings (Local)
        logger.info("Initializing Embeddings Model...")
        embeddings = HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL)
        
        # Initialize Pinecone client
        pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        index = pc.Index(settings.PINECONE_INDEX_NAME)
        
        # Process items and create vectors with unique IDs
        vectors_to_upsert = []
        batch_size = 100  # Pinecone recommends batches of 100
        total_vectors = 0
        
        for item in data:
            content = item.get("body", "")
            if not content:
                continue
                
            # Create a rich text representation for embedding
            date_str = item.get("date", "")
            subject = item.get("subject", "")
            sender = item.get("from", "")
            recipient = item.get("to", "")  # Get the To field
            email_id = item.get("email_id", hashlib.md5(content[:100].encode()).hexdigest())

            # Include To field in embedding so we can search by recipient
            full_text = f"Date: {date_str}\nFrom: {sender}\nTo: {recipient}\nSubject: {subject}\n\n{content}"
            chunks = text_splitter.split_text(full_text)
            
            for i, chunk in enumerate(chunks):
                # Create unique vector ID from email_id + chunk index
                vector_id = f"{upload_id}_{email_id}_{i}"
                
                # Generate embedding
                embedding = embeddings.embed_query(chunk)
                
                # Prepare metadata
                metadata = {
                    "upload_id": upload_id,
                    "email_id": email_id,
                    "date": date_str[:50] if date_str else "",  # Truncate long dates
                    "sender": sender[:100] if sender else "",   # Truncate long senders
                    "to": recipient[:200] if recipient else "",  # Store recipient for search
                    "subject": subject[:200] if subject else "",  # Truncate long subjects
                    "text": chunk[:1000],  # Store chunk text for retrieval (max 1000 chars)
                    "type": "email"
                }
                
                vectors_to_upsert.append({
                    "id": vector_id,
                    "values": embedding,
                    "metadata": metadata
                })
                
                # Upsert in batches
                if len(vectors_to_upsert) >= batch_size:
                    index.upsert(vectors=vectors_to_upsert)
                    total_vectors += len(vectors_to_upsert)
                    logger.info(f"Upserted {total_vectors} vectors so far...")
                    vectors_to_upsert = []
        
        # Upsert remaining vectors
        if vectors_to_upsert:
            index.upsert(vectors=vectors_to_upsert)
            total_vectors += len(vectors_to_upsert)

        if total_vectors == 0:
            logger.warning("No vectors to index.")
            return
            
        logger.info(f"Successfully indexed {total_vectors} vectors to Pinecone index '{settings.PINECONE_INDEX_NAME}'")
        
        # Mark as indexed
        mark_upload_indexed(upload_id, total_vectors)
        
        # Trigger Insights Generation
        from services.insights.processor import generate_insights
        generate_insights(upload_id)

    except Exception as e:
        logger.exception(f"Error indexing upload {upload_id}: {e}")


def get_index_stats() -> dict:
    """Get statistics about the Pinecone index."""
    try:
        pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        index = pc.Index(settings.PINECONE_INDEX_NAME)
        stats = index.describe_index_stats()
        return {
            "total_vectors": stats.total_vector_count,
            "dimension": stats.dimension
        }
    except Exception as e:
        logger.error(f"Error getting index stats: {e}")
        return {"error": str(e), "total_vectors": 0}
