"""
Embedding Service using Gemini
Handles text chunking and vector generation
"""
import re
from typing import List, Dict, Any, Tuple
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.config.settings import settings


class EmbeddingService:
    """Service for creating embeddings using Gemini"""
    
    def __init__(self, model: str = "models/embedding-001"):
        """
        Initialize embedding service
        
        Args:
            model: Gemini embedding model to use
        """
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set in environment variables")
        
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=model,
            google_api_key=settings.GEMINI_API_KEY
        )
        self.model = model
        print(f"✅ Embedding Service initialized with {model}")
    
    def chunk_text(
        self,
        text: str,
        chunk_size: int = 500,
        overlap: int = 100
    ) -> List[str]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Text to chunk
            chunk_size: Target size of each chunk (words)
            overlap: Number of words to overlap between chunks
        
        Returns:
            List of text chunks
        """
        if not text or len(text.strip()) == 0:
            return []
        
        # Split text into sentences first
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        chunks = []
        current_chunk = []
        current_word_count = 0
        
        for sentence in sentences:
            sentence_words = len(sentence.split())
            
            # Start new chunk if current one would exceed size
            if current_word_count + sentence_words > chunk_size and current_chunk:
                # Create chunk
                chunk_text = " ".join(current_chunk)
                if chunk_text.strip():
                    chunks.append(chunk_text)
                
                # Keep overlap
                overlap_text = " ".join(current_chunk[-(overlap // 10):]) if len(current_chunk) > 1 else ""
                current_chunk = [overlap_text] if overlap_text else []
                current_word_count = len(overlap_text.split()) if overlap_text else 0
            
            current_chunk.append(sentence)
            current_word_count += sentence_words
        
        # Add final chunk
        if current_chunk:
            chunk_text = " ".join(current_chunk)
            if chunk_text.strip():
                chunks.append(chunk_text)
        
        return chunks
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts
        
        Args:
            texts: List of text strings to embed
        
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        try:
            # Filter out empty texts
            valid_texts = [t.strip() for t in texts if t.strip()]
            
            if not valid_texts:
                return []
            
            # Generate embeddings
            embeddings = self.embeddings.embed_documents(valid_texts)
            
            return embeddings
        
        except Exception as e:
            print(f"❌ Error generating embeddings: {e}")
            raise
    
    def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for a single query
        
        Args:
            query: Query text to embed
        
        Returns:
            Embedding vector
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        
        try:
            embedding = self.embeddings.embed_query(query.strip())
            return embedding
        
        except Exception as e:
            print(f"❌ Error embedding query: {e}")
            raise
    
    def process_content(
        self,
        content: str,
        chunk_size: int = 500,
        overlap: int = 100
    ) -> Tuple[List[str], List[List[float]]]:
        """
        Process content: chunk and embed
        
        Args:
            content: Raw content to process
            chunk_size: Target chunk size in words
            overlap: Overlap between chunks in words
        
        Returns:
            Tuple of (chunks, embeddings)
        """
        # Chunk the text
        chunks = self.chunk_text(content, chunk_size, overlap)
        
        if not chunks:
            raise ValueError("No chunks generated from content")
        
        # Generate embeddings
        embeddings = self.generate_embeddings(chunks)
        
        if len(embeddings) != len(chunks):
            raise ValueError("Mismatch between chunks and embeddings")
        
        return chunks, embeddings


# Global embedding service instance
_embedding_service = None


def get_embedding_service() -> EmbeddingService:
    """Get or create global embedding service instance"""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service


def init_embedding_service(model: str = "models/embedding-001") -> EmbeddingService:
    """Initialize global embedding service"""
    global _embedding_service
    _embedding_service = EmbeddingService(model)
    return _embedding_service
