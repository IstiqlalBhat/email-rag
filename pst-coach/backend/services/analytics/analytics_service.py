"""
Analytics service for extracting visualization data from emails.
Provides data for timeline, word cloud, and network graph visualizations.
"""
from typing import List, Dict, Any, Optional
from collections import defaultdict, Counter
from datetime import datetime
import re
import json
import os

from loguru import logger
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone

from core.config import settings


# Common stop words to filter from word cloud
STOP_WORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of",
    "with", "by", "from", "as", "is", "was", "are", "were", "been", "be", "have",
    "has", "had", "do", "does", "did", "will", "would", "could", "should", "may",
    "might", "must", "can", "that", "this", "these", "those", "it", "its", "i",
    "you", "he", "she", "we", "they", "me", "him", "her", "us", "them", "my",
    "your", "his", "our", "their", "what", "which", "who", "whom", "when", "where",
    "why", "how", "all", "each", "every", "both", "few", "more", "most", "other",
    "some", "such", "no", "nor", "not", "only", "same", "so", "than", "too", "very",
    "just", "about", "if", "then", "also", "into", "out", "up", "down", "over",
    "under", "again", "further", "once", "here", "there", "am", "any", "re", "ve",
    "ll", "hi", "hello", "thanks", "thank", "please", "regards", "best", "sincerely",
    "sent", "received", "email", "subject", "mailto", "http", "https", "www", "com"
}


class AnalyticsService:
    """Service for computing analytics from email data."""
    
    def __init__(self):
        self._embeddings = None
        self._vector_store = None
        self._pc = None
    
    def _get_embeddings(self):
        if self._embeddings is None:
            self._embeddings = HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL)
        return self._embeddings
    
    def _get_vector_store(self) -> Optional[PineconeVectorStore]:
        if self._vector_store is None:
            try:
                self._pc = Pinecone(api_key=settings.PINECONE_API_KEY)
                existing_indexes = [idx.name for idx in self._pc.list_indexes()]
                
                if settings.PINECONE_INDEX_NAME in existing_indexes:
                    self._vector_store = PineconeVectorStore(
                        index_name=settings.PINECONE_INDEX_NAME,
                        embedding=self._get_embeddings(),
                        pinecone_api_key=settings.PINECONE_API_KEY
                    )
            except Exception as e:
                logger.error(f"Failed to connect to Pinecone: {e}")
        return self._vector_store
    
    def _get_pinecone_index(self):
        """Get direct Pinecone index for metadata queries."""
        if self._pc is None:
            self._pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        return self._pc.Index(settings.PINECONE_INDEX_NAME)
    
    async def get_timeline_data(self, upload_id: str) -> Dict[str, Any]:
        """
        Get email activity over time.
        Returns counts grouped by date for timeline visualization.
        """
        logger.info(f"Computing timeline data for upload_id: {upload_id}")
        
        try:
            vector_store = self._get_vector_store()
            if not vector_store:
                return {"dates": [], "counts": [], "error": "No data available"}
            
            # Query for a broad set of emails to analyze timeline
            results = vector_store.similarity_search(
                query="email communication",
                k=500,  # Get many results for meaningful timeline
                filter={"upload_id": upload_id} if upload_id else None
            )
            
            # Group by date
            date_counts = defaultdict(int)
            for doc in results:
                date_str = doc.metadata.get("date", "")
                if date_str:
                    # Parse and normalize to just date (YYYY-MM-DD)
                    try:
                        # Try common date formats
                        for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"]:
                            try:
                                dt = datetime.strptime(date_str.split()[0] if " " in date_str else date_str, fmt)
                                date_key = dt.strftime("%Y-%m-%d")
                                date_counts[date_key] += 1
                                break
                            except ValueError:
                                continue
                    except Exception:
                        # Skip unparseable dates
                        pass
            
            # Sort by date
            sorted_dates = sorted(date_counts.keys())
            
            return {
                "dates": sorted_dates,
                "counts": [date_counts[d] for d in sorted_dates],
                "total": sum(date_counts.values())
            }
            
        except Exception as e:
            logger.error(f"Error computing timeline: {e}")
            return {"dates": [], "counts": [], "error": str(e)}
    
    async def get_wordcloud_data(self, upload_id: str, top_n: int = 100) -> Dict[str, Any]:
        """
        Get word frequency data for word cloud visualization.
        Returns top N words with their counts.
        """
        logger.info(f"Computing word cloud data for upload_id: {upload_id}")
        
        try:
            vector_store = self._get_vector_store()
            if not vector_store:
                return {"words": [], "error": "No data available"}
            
            # Query for emails
            results = vector_store.similarity_search(
                query="important topics discussion",
                k=300,
                filter={"upload_id": upload_id} if upload_id else None
            )
            
            # Extract and count words
            word_counts = Counter()
            for doc in results:
                content = doc.page_content.lower()
                # Extract words (letters only, 3+ chars)
                words = re.findall(r'\b[a-z]{3,}\b', content)
                for word in words:
                    if word not in STOP_WORDS:
                        word_counts[word] += 1
            
            # Get top N words
            top_words = word_counts.most_common(top_n)
            
            return {
                "words": [{"text": word, "value": count} for word, count in top_words],
                "total_unique": len(word_counts)
            }
            
        except Exception as e:
            logger.error(f"Error computing word cloud: {e}")
            return {"words": [], "error": str(e)}
    
    async def get_network_data(self, upload_id: str) -> Dict[str, Any]:
        """
        Get relationship network data.
        Returns nodes (people) and edges (email connections) for network viz.
        """
        logger.info(f"Computing network data for upload_id: {upload_id}")
        
        try:
            vector_store = self._get_vector_store()
            if not vector_store:
                return {"nodes": [], "edges": [], "error": "No data available"}
            
            # Query for emails
            results = vector_store.similarity_search(
                query="communication conversation",
                k=500,
                filter={"upload_id": upload_id} if upload_id else None
            )
            
            # Build adjacency for email relationships
            # Format: {sender: {recipient: count}}
            connections = defaultdict(lambda: defaultdict(int))
            all_contacts = set()
            
            for doc in results:
                sender = doc.metadata.get("sender", "").strip()
                # Try to extract recipients from content (basic "Hi X" / "To: X" patterns)
                content = doc.page_content
                
                if sender:
                    all_contacts.add(sender)
                    # Count as connection to anyone mentioned
                    # Simple heuristic: look for "Hi [Name]" patterns
                    hi_matches = re.findall(r'(?:Hi|Hello|Dear)\s+([A-Z][a-z]+)', content)
                    for name in hi_matches:
                        connections[sender][name] += 1
                        all_contacts.add(name)
            
            # Build nodes and edges
            contact_list = list(all_contacts)
            node_index = {name: i for i, name in enumerate(contact_list)}
            
            nodes = [{"id": i, "name": name} for i, name in enumerate(contact_list)]
            
            edges = []
            for sender, recipients in connections.items():
                for recipient, count in recipients.items():
                    if sender in node_index and recipient in node_index:
                        edges.append({
                            "source": node_index[sender],
                            "target": node_index[recipient],
                            "weight": count
                        })
            
            return {
                "nodes": nodes,
                "edges": edges,
                "total_contacts": len(nodes),
                "total_connections": len(edges)
            }
            
        except Exception as e:
            logger.error(f"Error computing network: {e}")
            return {"nodes": [], "edges": [], "error": str(e)}


# Singleton instance
analytics_service = AnalyticsService()
