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
from services.cache.redis_service import redis_service


# Analytics cache TTL (10 minutes)
ANALYTICS_CACHE_TTL = 600


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
        # Check cache first
        cache_key = f"analytics:timeline:{upload_id}"
        cached = await redis_service.get_cached(cache_key)
        if cached:
            logger.info(f"Cache hit for timeline data: {upload_id}")
            return cached
        
        logger.info(f"Computing timeline data for upload_id: {upload_id}")
        
        try:
            vector_store = self._get_vector_store()
            if not vector_store:
                return {"dates": [], "counts": [], "error": "No data available"}
            
            # Query for a broad set of emails to analyze timeline
            # Note: LangChain PineconeVectorStore filter may not work perfectly
            # so we query broadly and filter locally
            results = vector_store.similarity_search(
                query="email communication",
                k=500,  # Get many results for meaningful timeline
            )
            
            # Filter by upload_id locally if provided
            if upload_id:
                results = [r for r in results if r.metadata.get("upload_id") == upload_id]
            
            # Group by date
            date_counts = defaultdict(int)
            for doc in results:
                date_str = doc.metadata.get("date", "")
                if date_str:
                    # Parse and normalize to just date (YYYY-MM-DD)
                    # Handle various formats including Outlook's "Monday, September 9, 2024 9:22 AM"
                    try:
                        # Date formats to try
                        formats = [
                            "%A, %B %d, %Y %I:%M %p",      # Monday, September 9, 2024 9:22 AM
                            "%A, %B %d, %Y %I:%M:%S %p",   # Monday, September 9, 2024 9:22:00 AM
                            "%A, %B %d, %Y",               # Monday, September 9, 2024
                            "%B %d, %Y %I:%M %p",          # September 9, 2024 9:22 AM
                            "%B %d, %Y",                   # September 9, 2024
                            "%Y-%m-%d %H:%M:%S",           # 2024-09-09 09:22:00
                            "%Y-%m-%d",                    # 2024-09-09
                            "%m/%d/%Y",                    # 09/09/2024
                            "%d/%m/%Y",                    # 09/09/2024
                        ]
                        
                        parsed = False
                        for fmt in formats:
                            try:
                                dt = datetime.strptime(date_str.strip()[:50], fmt)
                                date_key = dt.strftime("%Y-%m-%d")
                                date_counts[date_key] += 1
                                parsed = True
                                break
                            except ValueError:
                                continue
                        
                        if not parsed:
                            # Try extracting date with regex as fallback
                            import re
                            month_match = re.search(r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(\d{4})', date_str)
                            if month_match:
                                month_str = month_match.group(1)
                                day = int(month_match.group(2))
                                year = int(month_match.group(3))
                                months = {"January":1,"February":2,"March":3,"April":4,"May":5,"June":6,
                                         "July":7,"August":8,"September":9,"October":10,"November":11,"December":12}
                                month = months.get(month_str, 1)
                                date_key = f"{year}-{month:02d}-{day:02d}"
                                date_counts[date_key] += 1
                                
                    except Exception:
                        # Skip unparseable dates
                        pass
            
            # Sort by date
            sorted_dates = sorted(date_counts.keys())
            
            result = {
                "dates": sorted_dates,
                "counts": [date_counts[d] for d in sorted_dates],
                "total": sum(date_counts.values())
            }
            
            # Cache the result
            await redis_service.set_cached(cache_key, result, ANALYTICS_CACHE_TTL)
            return result
            
        except Exception as e:
            logger.error(f"Error computing timeline: {e}")
            return {"dates": [], "counts": [], "error": str(e)}
    
    async def get_wordcloud_data(self, upload_id: str, top_n: int = 100) -> Dict[str, Any]:
        """
        Get word frequency data for word cloud visualization.
        Returns top N words with their counts.
        """
        # Check cache first
        cache_key = f"analytics:wordcloud:{upload_id}:{top_n}"
        cached = await redis_service.get_cached(cache_key)
        if cached:
            logger.info(f"Cache hit for wordcloud data: {upload_id}")
            return cached
        
        logger.info(f"Computing word cloud data for upload_id: {upload_id}")
        
        try:
            vector_store = self._get_vector_store()
            if not vector_store:
                return {"words": [], "error": "No data available"}
            
            # Query for emails (filter locally since LangChain filter may not work)
            results = vector_store.similarity_search(
                query="important topics discussion",
                k=500,
            )
            
            # Filter by upload_id locally if provided
            if upload_id:
                results = [r for r in results if r.metadata.get("upload_id") == upload_id]
            
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
            
            result = {
                "words": [{"text": word, "value": count} for word, count in top_words],
                "total_unique": len(word_counts)
            }
            
            # Cache the result
            await redis_service.set_cached(cache_key, result, ANALYTICS_CACHE_TTL)
            return result
            
        except Exception as e:
            logger.error(f"Error computing word cloud: {e}")
            return {"words": [], "error": str(e)}
    
    async def get_network_data(self, upload_id: str) -> Dict[str, Any]:
        """
        Get relationship network data.
        Returns nodes (people) and edges (email connections) for network viz.
        """
        # Check cache first
        cache_key = f"analytics:network:{upload_id}"
        cached = await redis_service.get_cached(cache_key)
        if cached:
            logger.info(f"Cache hit for network data: {upload_id}")
            return cached
        
        logger.info(f"Computing network data for upload_id: {upload_id}")
        
        try:
            vector_store = self._get_vector_store()
            if not vector_store:
                return {"nodes": [], "edges": [], "error": "No data available"}
            
            # Query for emails (filter locally since LangChain filter may not work)
            results = vector_store.similarity_search(
                query="communication conversation",
                k=500,
            )
            
            # Filter by upload_id locally if provided
            if upload_id:
                results = [r for r in results if r.metadata.get("upload_id") == upload_id]
            
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
            
            result = {
                "nodes": nodes,
                "edges": edges,
                "total_contacts": len(nodes),
                "total_connections": len(edges)
            }
            
            # Cache the result
            await redis_service.set_cached(cache_key, result, ANALYTICS_CACHE_TTL)
            return result
            
        except Exception as e:
            logger.error(f"Error computing network: {e}")
            return {"nodes": [], "edges": [], "error": str(e)}


# Singleton instance
analytics_service = AnalyticsService()
