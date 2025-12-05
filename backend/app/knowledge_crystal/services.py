"""
Knowledge Crystal Services
Core business logic for KB operations
"""
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from .models import (
    KBPageCreate, KBPageUpdate, KBPageResponse,
    SearchQuery, SearchResult, QueryRequest, QueryResponse
)
from .embedding_service import get_embedding_service
from .vector_store import get_vector_store


class KBPageService:
    """Service for managing knowledge pages"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection: AsyncIOMotorCollection = db["kb_pages"]
    
    async def create_page(self, page_data: KBPageCreate) -> Dict[str, Any]:
        """
        Create a new knowledge page and generate embeddings
        
        Args:
            page_data: KB page creation data
        
        Returns:
            Created page document
        """
        embedding_service = get_embedding_service()
        vector_store = get_vector_store()
        
        # Process content: chunk and embed
        try:
            chunks, embeddings = embedding_service.process_content(page_data.content)
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to process content: {str(e)}"
            }
        
        # Create page document
        page_doc = {
            "_id": ObjectId(),
            "title": page_data.title,
            "content": page_data.content,
            "tags": page_data.tags,
            "visibility": page_data.visibility,
            "author": page_data.author,
            "metadata": page_data.metadata or {},
            "status": "indexing",
            "chunk_count": len(chunks),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Save page to MongoDB
        result = await self.collection.insert_one(page_doc)
        page_id = str(result.inserted_id)
        
        # Add chunks to vector store
        metadata = [
            {
                "visibility": page_data.visibility,
                "author": page_data.author,
                "tags": page_data.tags
            }
            for _ in chunks
        ]
        
        vector_result = vector_store.add_chunks(
            page_id=page_id,
            chunks=chunks,
            title=page_data.title,
            embeddings=embeddings,
            metadata=metadata
        )
        
        if not vector_result.get("success"):
            # Update status to error
            await self.collection.update_one(
                {"_id": result.inserted_id},
                {"$set": {"status": "error"}}
            )
            return {
                "success": False,
                "error": f"Failed to index chunks: {vector_result.get('error')}"
            }
        
        # Update status to indexed
        await self.collection.update_one(
            {"_id": result.inserted_id},
            {"$set": {"status": "indexed"}}
        )
        
        return {
            "success": True,
            "page_id": page_id,
            "chunks_created": len(chunks),
            "title": page_data.title,
            "created_at": page_doc["created_at"]
        }
    
    async def get_page(self, page_id: str) -> Optional[Dict[str, Any]]:
        """Get a knowledge page by ID"""
        try:
            page = await self.collection.find_one({"_id": ObjectId(page_id)})
            if page:
                page["_id"] = str(page["_id"])
            return page
        except Exception as e:
            print(f"❌ Error fetching page: {e}")
            return None
    
    async def update_page(self, page_id: str, update_data: KBPageUpdate) -> Dict[str, Any]:
        """
        Update a knowledge page (re-indexes if content changed)
        
        Args:
            page_id: ID of page to update
            update_data: Update data
        
        Returns:
            Update result
        """
        embedding_service = get_embedding_service()
        vector_store = get_vector_store()
        
        # Get existing page
        existing_page = await self.get_page(page_id)
        if not existing_page:
            return {"success": False, "error": "Page not found"}
        
        # If content changed, re-index
        if update_data.content and update_data.content != existing_page.get("content"):
            # Delete old chunks
            vector_store.delete_chunks(page_id)
            
            # Generate new chunks and embeddings
            try:
                chunks, embeddings = embedding_service.process_content(update_data.content)
            except Exception as e:
                return {"success": False, "error": f"Failed to process content: {str(e)}"}
            
            # Add new chunks
            title = update_data.title or existing_page.get("title")
            metadata = [
                {
                    "visibility": update_data.visibility or existing_page.get("visibility"),
                    "author": existing_page.get("author"),
                    "tags": update_data.tags or existing_page.get("tags")
                }
                for _ in chunks
            ]
            
            vector_result = vector_store.add_chunks(
                page_id=page_id,
                chunks=chunks,
                title=title,
                embeddings=embeddings,
                metadata=metadata
            )
            
            if not vector_result.get("success"):
                return {"success": False, "error": "Failed to re-index content"}
        
        # Update MongoDB document
        update_fields = {}
        if update_data.title:
            update_fields["title"] = update_data.title
        if update_data.content:
            update_fields["content"] = update_data.content
        if update_data.tags is not None:
            update_fields["tags"] = update_data.tags
        if update_data.visibility:
            update_fields["visibility"] = update_data.visibility
        if update_data.metadata:
            update_fields["metadata"] = update_data.metadata
        
        update_fields["updated_at"] = datetime.utcnow()
        
        result = await self.collection.update_one(
            {"_id": ObjectId(page_id)},
            {"$set": update_fields}
        )
        
        return {
            "success": True,
            "modified_count": result.modified_count,
            "page_id": page_id
        }
    
    async def delete_page(self, page_id: str) -> Dict[str, Any]:
        """Delete a knowledge page and its chunks"""
        vector_store = get_vector_store()
        
        # Delete chunks from vector store
        vector_store.delete_chunks(page_id)
        
        # Delete from MongoDB
        result = await self.collection.delete_one({"_id": ObjectId(page_id)})
        
        return {
            "success": True,
            "deleted_count": result.deleted_count
        }
    
    async def list_pages(
        self,
        visibility: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 10,
        skip: int = 0
    ) -> Dict[str, Any]:
        """List knowledge pages with optional filters"""
        query = {}
        
        if visibility:
            query["visibility"] = visibility
        
        if tags:
            query["tags"] = {"$in": tags}
        
        pages = await self.collection.find(query) \
            .skip(skip) \
            .limit(limit) \
            .to_list(length=limit)
        
        total = await self.collection.count_documents(query)
        
        # Convert ObjectId to string
        for page in pages:
            page["_id"] = str(page["_id"])
        
        return {
            "pages": pages,
            "total": total,
            "limit": limit,
            "skip": skip
        }


class KBSearchService:
    """Service for semantic search"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.page_collection: AsyncIOMotorCollection = db["kb_pages"]
    
    async def search(
        self,
        query: SearchQuery,
        limit: int = 5
    ) -> List[SearchResult]:
        """
        Perform semantic search on knowledge pages
        
        Args:
            query: Search query
            limit: Number of results to return
        
        Returns:
            List of search results
        """
        embedding_service = get_embedding_service()
        vector_store = get_vector_store()
        
        # Generate query embedding
        try:
            query_embedding = embedding_service.embed_query(query.query)
        except Exception as e:
            print(f"❌ Failed to embed query: {e}")
            return []
        
        # Search vector store
        chunks = vector_store.search(query_embedding, limit=limit)
        
        results = []
        for chunk in chunks:
            metadata = chunk.get("metadata", {})
            page_id = metadata.get("page_id")
            
            # Get page details
            page = await self.page_collection.find_one({"_id": ObjectId(page_id)})
            if not page:
                continue
            
            result = SearchResult(
                page_id=str(page["_id"]),
                title=page.get("title", ""),
                content=page.get("content", "")[:1000],  # Truncate long content
                tags=page.get("tags", []),
                chunk_snippet=chunk.get("content", "")[:500],
                similarity_score=chunk.get("similarity_score", 0),
                author=page.get("author", "unknown")
            )
            results.append(result)
        
        return results


class KBRAGService:
    """Service for Retrieval-Augmented Generation (Q&A)"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.page_collection: AsyncIOMotorCollection = db["kb_pages"]
        self.search_service = KBSearchService(db)
    
    async def query(self, query_req: QueryRequest) -> QueryResponse:
        """
        Answer a question using RAG pipeline
        
        Args:
            query_req: Query request with question
        
        Returns:
            Query response with answer and sources
        """
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        # Search for relevant chunks
        search_query = SearchQuery(
            query=query_req.question,
            limit=query_req.limit,
            tags=query_req.tags,
            visibility=query_req.visibility
        )
        
        sources = await self.search_service.search(search_query, limit=query_req.limit)
        
        if not sources:
            return QueryResponse(
                answer="No relevant information found in the knowledge base.",
                sources=[],
                confidence=0.0,
                model_used=settings.GEMINI_MODEL
            )
        
        # Prepare context from retrieved chunks
        context = "\n".join([
            f"[Source: {s.title}]\n{s.chunk_snippet}\n"
            for s in sources
        ])
        
        # Create RAG prompt
        rag_prompt = f"""You are a helpful assistant. Answer the following question using ONLY the provided context. 
If the answer is not in the context, say "I don't have enough information to answer this question."

Context:
{context}

Question: {query_req.question}

Please provide a clear, concise answer citing the relevant sources."""
        
        try:
            # Generate answer using Gemini
            llm = ChatGoogleGenerativeAI(
                model=settings.GEMINI_MODEL,
                google_api_key=settings.GEMINI_API_KEY
            )
            
            response = llm.invoke(rag_prompt)
            answer = response.content if hasattr(response, 'content') else str(response)
            
            # Calculate confidence based on similarity scores
            avg_confidence = sum(s.similarity_score for s in sources) / len(sources) if sources else 0
            
            return QueryResponse(
                answer=answer,
                sources=sources,
                confidence=min(1.0, avg_confidence),
                model_used=settings.GEMINI_MODEL
            )
        
        except Exception as e:
            print(f"❌ Error generating answer: {e}")
            return QueryResponse(
                answer=f"Error generating answer: {str(e)}",
                sources=sources,
                confidence=0.0,
                model_used=settings.GEMINI_MODEL
            )


# Import settings at end to avoid circular imports
from app.config.settings import settings
