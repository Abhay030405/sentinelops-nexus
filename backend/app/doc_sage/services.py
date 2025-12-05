"""
Document Services Module
Handles all document operations: creation, retrieval, search, and deletion
"""

import logging
import os
from datetime import datetime
from typing import List, Optional
from bson import ObjectId
from app.database.mongodb import get_database
from app.doc_sage.ai_processor import get_ai_processor
from app.doc_sage.text_extractor import extract_text

logger = logging.getLogger(__name__)


class DocumentService:
    """Service for document operations"""
    
    COLLECTION_NAME = "documents"
    
    @classmethod
    async def create_document(
        cls,
        filename: str,
        file_path: str,
        file_size: int,
        mime_type: str,
        uploaded_by: str = "Current Ranger"
    ) -> dict:
        """Create document record in database"""
        try:
            db = get_database()
            collection = db[cls.COLLECTION_NAME]
            
            document = {
                "name": filename,
                "file_path": file_path,
                "file_size": file_size,
                "mime_type": mime_type,
                "status": "processing",
                "uploaded_by": uploaded_by,
                "uploaded_at": datetime.utcnow(),
                "extracted_text": None,
                "summary": {
                    "short_summary": None,
                    "long_summary": None,
                    "keywords": []
                },
                "processed_at": None
            }
            
            result = await collection.insert_one(document)
            
            logger.info(f"📝 Created document record: {result.inserted_id}")
            return {
                "_id": str(result.inserted_id),
                "name": filename,
                "status": "processing",
                "uploaded_at": document["uploaded_at"],
                "uploaded_by": document["uploaded_by"]
            }
        
        except Exception as e:
            logger.error(f"❌ Error creating document: {e}")
            raise
    
    @classmethod
    async def get_document(cls, doc_id: str) -> Optional[dict]:
        """Get document by ID"""
        try:
            db = get_database()
            collection = db[cls.COLLECTION_NAME]
            doc = await collection.find_one({"_id": ObjectId(doc_id)})
            if doc:
                doc["_id"] = str(doc["_id"])
            return doc
        
        except Exception as e:
            logger.error(f"❌ Error getting document: {e}")
            raise
    
    @classmethod
    async def get_all_documents(cls) -> List[dict]:
        """Get all documents"""
        try:
            db = get_database()
            collection = db[cls.COLLECTION_NAME]
            docs = await collection.find().sort("uploaded_at", -1).to_list(None)
            
            # Convert ObjectIds to strings for Pydantic serialization
            for doc in docs:
                doc["_id"] = str(doc["_id"])
            
            return docs
        
        except Exception as e:
            logger.error(f"❌ Error getting documents: {e}")
            raise
    
    @classmethod
    async def update_document_status(cls, doc_id: str, **fields) -> bool:
        """Update document with fields"""
        try:
            db = get_database()
            collection = db[cls.COLLECTION_NAME]
            
            update_data = {**fields}
            result = await collection.update_one(
                {"_id": ObjectId(doc_id)},
                {"$set": update_data}
            )
            
            return result.modified_count > 0
        
        except Exception as e:
            logger.error(f"❌ Error updating document: {e}")
            raise
    
    @classmethod
    async def process_document_text(cls, doc_id: str) -> bool:
        """Process document: extract text and generate AI summary"""
        try:
            logger.info(f"🔄 Processing document: {doc_id}")
            
            doc = await cls.get_document(doc_id)
            if not doc:
                logger.error(f"Document not found: {doc_id}")
                return False
            
            logger.info("📄 Extracting text...")
            text = await extract_text(doc["file_path"], doc["mime_type"])
            
            logger.info("🤖 Processing with AI...")
            ai_processor = get_ai_processor()
            ai_result = ai_processor.process_document(text)
            
            await cls.update_document_status(
                doc_id,
                extracted_text=text,
                summary=ai_result,
                status="processed",
                processed_at=datetime.utcnow()
            )
            
            logger.info(f"✅ Document processed: {doc_id}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Error processing document: {e}")
            await cls.update_document_status(doc_id, status="error", error_message=str(e))
            return False
    
    @classmethod
    async def search_documents(cls, query: str) -> List[dict]:
        """Search documents by text, keywords, or name"""
        try:
            logger.info(f"🔍 Searching for: {query}")
            
            db = get_database()
            collection = db[cls.COLLECTION_NAME]
            
            search_filter = {
                "$or": [
                    {"name": {"$regex": query, "$options": "i"}},
                    {"extracted_text": {"$regex": query, "$options": "i"}},
                    {"summary.keywords": {"$regex": query, "$options": "i"}},
                    {"summary.short_summary": {"$regex": query, "$options": "i"}}
                ],
                "status": "processed"
            }
            
            results = await collection.find(search_filter).to_list(None)
            
            # Convert ObjectIds to strings for Pydantic serialization
            for doc in results:
                doc["_id"] = str(doc["_id"])
            
            logger.info(f"✅ Found {len(results)} matching documents")
            return results
        
        except Exception as e:
            logger.error(f"❌ Error searching: {e}")
            raise
    
    @classmethod
    async def delete_document(cls, doc_id: str) -> bool:
        """Delete document and file"""
        try:
            doc = await cls.get_document(doc_id)
            if not doc:
                return False
            
            if os.path.exists(doc["file_path"]):
                os.remove(doc["file_path"])
                logger.info(f"🗑️ Deleted file: {doc['file_path']}")
            
            db = get_database()
            collection = db[cls.COLLECTION_NAME]
            result = await collection.delete_one({"_id": ObjectId(doc_id)})
            
            logger.info(f"✅ Deleted document: {doc_id}")
            return result.deleted_count > 0
        
        except Exception as e:
            logger.error(f"❌ Error deleting: {e}")
            raise


document_service = DocumentService()