"""
Rebuild Pinecone Index Script

This script rebuilds the Pinecone index from extracted email data.
It uses the same indexing logic as the main service but can be run independently.
"""

import os
import sys
import json
import hashlib
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loguru import logger
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from pinecone import Pinecone, ServerlessSpec

from core.config import settings

# Configure logger
logger.add("logs/indexing.log", rotation="10 MB")


def ensure_pinecone_index(pc: Pinecone, delete_existing: bool = False) -> bool:
    """Ensure Pinecone index exists, optionally delete and recreate."""
    try:
        existing_indexes = [idx.name for idx in pc.list_indexes()]
        
        if settings.PINECONE_INDEX_NAME in existing_indexes:
            if delete_existing:
                logger.info(f"Deleting existing Pinecone index: {settings.PINECONE_INDEX_NAME}")
                pc.delete_index(settings.PINECONE_INDEX_NAME)
                import time
                time.sleep(5)  # Wait for deletion to complete
            else:
                logger.info(f"Pinecone index already exists: {settings.PINECONE_INDEX_NAME}")
                return True
        
        logger.info(f"Creating Pinecone index: {settings.PINECONE_INDEX_NAME}")
        pc.create_index(
            name=settings.PINECONE_INDEX_NAME,
            dimension=settings.EMBEDDING_DIMENSION,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
        
        # Wait for index to be ready
        import time
        time.sleep(10)
        
        logger.info("Pinecone index created successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to ensure Pinecone index: {e}")
        return False


def index_emails(emails: list, upload_id: str) -> int:
    """
    Index emails to Pinecone.
    Returns the number of vectors indexed.
    """
    logger.info(f"Starting indexing of {len(emails)} emails")
    
    # Initialize embeddings
    logger.info(f"Initializing embeddings model: {settings.EMBEDDING_MODEL}")
    embeddings = HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL)
    
    # Initialize text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP
    )
    
    # Initialize Pinecone
    logger.info("Connecting to Pinecone...")
    pc = Pinecone(api_key=settings.PINECONE_API_KEY)
    
    # Ensure index exists (recreate to ensure clean slate)
    if not ensure_pinecone_index(pc, delete_existing=True):
        logger.error("Failed to create Pinecone index")
        return 0
    
    index = pc.Index(settings.PINECONE_INDEX_NAME)
    
    # Process emails and create vectors
    vectors_to_upsert = []
    batch_size = 100
    total_vectors = 0
    
    for i, email in enumerate(emails):
        body = email.get("body", "")
        if not body or len(body) < 10:
            continue
        
        # Get metadata
        date_str = email.get("date", "")
        subject = email.get("subject", "")
        sender = email.get("from", "")
        recipient = email.get("to", "")
        cc = email.get("cc", "")
        email_id = email.get("email_id", hashlib.md5(body[:100].encode()).hexdigest())
        
        # Create rich text for embedding that includes all metadata
        # This makes the email searchable by sender, recipient, AND content
        full_text = f"Date: {date_str}\nFrom: {sender}\nTo: {recipient}\nSubject: {subject}\n\n{body}"
        
        # Split into chunks
        chunks = text_splitter.split_text(full_text)
        
        for chunk_idx, chunk in enumerate(chunks):
            # Create unique vector ID
            vector_id = f"{upload_id}_{email_id}_{chunk_idx}"
            
            # Generate embedding
            embedding = embeddings.embed_query(chunk)
            
            # Prepare metadata (Pinecone has size limits)
            metadata = {
                "upload_id": upload_id,
                "email_id": email_id,
                "date": date_str[:50] if date_str else "",
                "sender": sender[:150] if sender else "",
                "to": recipient[:300] if recipient else "",
                "cc": cc[:200] if cc else "",
                "subject": subject[:200] if subject else "",
                "text": chunk[:2000],  # Store chunk text for retrieval
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
                logger.info(f"Indexed {total_vectors} vectors ({i+1}/{len(emails)} emails)...")
                vectors_to_upsert = []
    
    # Upsert remaining vectors
    if vectors_to_upsert:
        index.upsert(vectors=vectors_to_upsert)
        total_vectors += len(vectors_to_upsert)
    
    logger.info(f"Indexing complete! Total vectors: {total_vectors}")
    return total_vectors


def mark_upload_indexed(upload_id: str, vector_count: int):
    """Mark an upload as indexed."""
    indexed_file = os.path.join(settings.DATA_DIR, "indexed_uploads.json")
    
    indexed = {}
    if os.path.exists(indexed_file):
        try:
            with open(indexed_file, "r") as f:
                indexed = json.load(f)
        except:
            pass
    
    indexed[upload_id] = {
        "vector_count": vector_count,
        "indexed_at": str(datetime.now())
    }
    
    os.makedirs(os.path.dirname(indexed_file), exist_ok=True)
    with open(indexed_file, "w") as f:
        json.dump(indexed, f, indent=2)
    
    logger.info(f"Marked upload {upload_id} as indexed with {vector_count} vectors")


def main():
    """Main function to rebuild the Pinecone index."""
    
    # Find extracted email files
    extracted_dir = settings.EXTRACTED_DIR
    if not os.path.exists(extracted_dir):
        print(f"❌ Extracted directory not found: {extracted_dir}")
        return
    
    # Find all JSON files (excluding analysis files)
    json_files = [f for f in os.listdir(extracted_dir) 
                  if f.endswith('.json') and not f.endswith('_analysis.json')]
    
    if not json_files:
        print("❌ No extracted email files found")
        return
    
    print(f"📁 Found {len(json_files)} extracted email files:")
    for f in json_files:
        print(f"   - {f}")
    
    # Check Pinecone API key
    if not settings.PINECONE_API_KEY:
        print("❌ PINECONE_API_KEY not set in environment")
        return
    
    print(f"\n🔑 Pinecone API Key: {settings.PINECONE_API_KEY[:10]}...")
    print(f"📊 Pinecone Index: {settings.PINECONE_INDEX_NAME}")
    print(f"📏 Embedding Dimension: {settings.EMBEDDING_DIMENSION}")
    print(f"🤖 Embedding Model: {settings.EMBEDDING_MODEL}")
    
    total_emails = 0
    total_vectors = 0
    
    for json_file in json_files:
        file_path = os.path.join(extracted_dir, json_file)
        upload_id = json_file.replace('.json', '')
        
        print(f"\n📧 Processing: {json_file}")
        
        # Load emails
        with open(file_path, 'r', encoding='utf-8') as f:
            emails = json.load(f)
        
        print(f"   Loaded {len(emails)} emails")
        total_emails += len(emails)
        
        # Index to Pinecone
        print("   🔄 Indexing to Pinecone...")
        vector_count = index_emails(emails, upload_id)
        total_vectors += vector_count
        
        # Mark as indexed
        mark_upload_indexed(upload_id, vector_count)
        
        print(f"   ✅ Indexed {vector_count} vectors")
    
    print(f"\n" + "="*50)
    print(f"✅ INDEXING COMPLETE!")
    print(f"   Total emails: {total_emails}")
    print(f"   Total vectors: {total_vectors}")
    print(f"="*50)


if __name__ == "__main__":
    main()
