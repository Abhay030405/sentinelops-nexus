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
        uploaded_by: str = "Current Ranger",
        mission_id: Optional[str] = None,
        allowed_users: List[str] = None
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
                "mission_id": mission_id,
                "allowed_users": allowed_users or [],
                "extracted_text": None,
                "summary": {
                    "short_summary": None,
                    "long_summary": None,
                    "keywords": [],
                    "tag_suggestions": [],
                    "page_summaries": []
                },
                "insights": {
                    "total_pages": 0,
                    "word_count": 0,
                    "estimated_read_time": 0,
                    "document_type": None,
                    "key_entities": [],
                    "important_sections": []
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
                "uploaded_by": document["uploaded_by"],
                "mission_id": mission_id
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
    async def get_all_documents(cls, user_email: Optional[str] = None) -> List[dict]:
        """Get all documents (filtered by access if user_email provided)"""
        try:
            db = get_database()
            collection = db[cls.COLLECTION_NAME]
            
            query = {}
            if user_email:
                query = {
                    "$or": [
                        {"uploaded_by": user_email},
                        {"allowed_users": user_email},
                        {"allowed_users": {"$size": 0}}  # Documents with no restrictions
                    ]
                }
            
            docs = await collection.find(query).sort("uploaded_at", -1).to_list(None)
            
            # Convert ObjectIds to strings for Pydantic serialization
            for doc in docs:
                doc["_id"] = str(doc["_id"])
            
            return docs
        
        except Exception as e:
            logger.error(f"❌ Error getting documents: {e}")
            raise
    
    @classmethod
    async def get_documents_by_mission(cls, mission_id: str, user_email: Optional[str] = None) -> List[dict]:
        """Get all documents for a specific mission"""
        try:
            db = get_database()
            collection = db[cls.COLLECTION_NAME]
            
            query = {"mission_id": mission_id}
            if user_email:
                query["$or"] = [
                    {"uploaded_by": user_email},
                    {"allowed_users": user_email}
                ]
            
            docs = await collection.find(query).sort("uploaded_at", -1).to_list(None)
            
            for doc in docs:
                doc["_id"] = str(doc["_id"])
            
            return docs
        
        except Exception as e:
            logger.error(f"❌ Error getting mission documents: {e}")
            raise
    
    @classmethod
    async def check_document_access(cls, doc_id: str, user_email: str) -> bool:
        """Check if user has access to document"""
        try:
            doc = await cls.get_document(doc_id)
            if not doc:
                return False
            
            # Admin/uploader always has access
            if doc.get("uploaded_by") == user_email:
                return True
            
            # Check allowed users list
            allowed_users = doc.get("allowed_users", [])
            if not allowed_users:  # Empty list means public
                return True
            
            return user_email in allowed_users
        
        except Exception as e:
            logger.error(f"❌ Error checking access: {e}")
            return False
    
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
        """Process document: extract text and generate AI summary with insights"""
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
            
            # Generate summary and tags
            ai_result = ai_processor.process_document(text)
            
            # Generate insights
            logger.info("📊 Generating insights...")
            insights = ai_processor.generate_document_insights(text)
            
            await cls.update_document_status(
                doc_id,
                extracted_text=text,
                summary=ai_result,
                insights=insights,
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


class ChatService:
    """Service for document chat functionality"""
    
    COLLECTION_NAME = "document_chats"
    
    @classmethod
    async def get_or_create_chat_history(cls, document_id: str, user_id: str, mission_id: Optional[str] = None) -> dict:
        """Get existing chat history or create new one"""
        try:
            db = get_database()
            collection = db[cls.COLLECTION_NAME]
            
            chat = await collection.find_one({
                "document_id": document_id,
                "user_id": user_id
            })
            
            if not chat:
                chat = {
                    "document_id": document_id,
                    "mission_id": mission_id,
                    "user_id": user_id,
                    "messages": [],
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                result = await collection.insert_one(chat)
                chat["_id"] = str(result.inserted_id)
            else:
                chat["_id"] = str(chat["_id"])
            
            return chat
        
        except Exception as e:
            logger.error(f"❌ Error getting chat history: {e}")
            raise
    
    @classmethod
    async def add_message(cls, document_id: str, user_id: str, role: str, content: str) -> bool:
        """Add a message to chat history"""
        try:
            db = get_database()
            collection = db[cls.COLLECTION_NAME]
            
            message = {
                "role": role,
                "content": content,
                "timestamp": datetime.utcnow()
            }
            
            result = await collection.update_one(
                {"document_id": document_id, "user_id": user_id},
                {
                    "$push": {"messages": message},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            
            return result.modified_count > 0
        
        except Exception as e:
            logger.error(f"❌ Error adding message: {e}")
            raise
    
    @classmethod
    async def answer_question(cls, document_id: str, user_id: str, question: str, include_history: bool = True) -> dict:
        """Answer a question about the document using AI"""
        try:
            # Get document
            doc = await DocumentService.get_document(document_id)
            if not doc:
                raise ValueError("Document not found")
            
            if doc.get("status") != "processed":
                raise ValueError("Document is not yet processed")
            
            # Get chat history
            chat_history = await cls.get_or_create_chat_history(document_id, user_id, doc.get("mission_id"))
            
            # Add user message
            await cls.add_message(document_id, user_id, "user", question)
            
            # Get AI processor
            ai_processor = get_ai_processor()
            
            # Build context
            context = doc.get("extracted_text", "")[:10000]  # Limit context size
            history_context = ""
            
            if include_history and chat_history.get("messages"):
                recent_messages = chat_history["messages"][-6:]  # Last 3 exchanges
                history_context = "\n".join([
                    f"{msg['role']}: {msg['content']}" 
                    for msg in recent_messages
                ])
            
            # Generate answer
            answer = ai_processor.answer_document_question(
                question=question,
                document_context=context,
                chat_history=history_context
            )
            
            # Add assistant message
            await cls.add_message(document_id, user_id, "assistant", answer)
            
            logger.info(f"✅ Generated answer for document {document_id}")
            return {
                "answer": answer,
                "sources": [doc.get("name")],
                "timestamp": datetime.utcnow()
            }
        
        except Exception as e:
            logger.error(f"❌ Error answering question: {e}")
            raise
    
    @classmethod
    async def get_chat_history(cls, document_id: str, user_id: str) -> dict:
        """Get chat history for a document"""
        try:
            chat = await cls.get_or_create_chat_history(document_id, user_id)
            return chat
        
        except Exception as e:
            logger.error(f"❌ Error getting chat history: {e}")
            raise


document_service = DocumentService()
chat_service = ChatService()