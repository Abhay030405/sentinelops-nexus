# 📄 Doc-Sage - AI-Powered Document Processing System

## Overview

Doc-Sage is an intelligent document processing system that allows admins to upload documents for missions, process them with AI, and enable both admins and assigned agents to interact with documents through an AI chatbot.

## 🎯 Key Features

### 1. Mission-Based Document Management
- **Upload documents** linked to specific missions
- **Access Control**: Only admin and assigned agents can view mission documents
- **Automatic Organization**: Documents stored in mission-specific folders

### 2. AI-Powered Processing
- **Text Extraction**: From PDF, images (OCR), and text files
- **Smart Summaries**: 
  - Short summary (quick overview)
  - Long summary (detailed analysis)
- **Keyword Extraction**: Automatically identifies key terms
- **Tag Suggestions**: AI suggests relevant tags for categorization
- **Document Insights**:
  - Document type detection
  - Word count & estimated read time
  - Key entities identification
  - Important sections highlighting

### 3. AI Chatbot with History
- **Ask Questions**: Chat with the document using natural language
- **Context Awareness**: AI remembers previous conversation
- **Source References**: Answers include document references
- **Chat History**: Persistent conversation storage per user

### 4. Access Control
- **Admin Access**: Full access to all documents they upload
- **Agent Access**: Only documents from assigned missions
- **User-Based Filtering**: Automatic filtering based on user permissions

## 🔧 API Endpoints

### Document Upload & Management

#### Upload Document
```http
POST /api/docsage/upload
Content-Type: multipart/form-data

Parameters:
- file: File (required)
- mission_id: string (optional)
- uploaded_by: string (email)
- allowed_users: string (comma-separated emails)
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/docsage/upload" \
  -F "file=@document.pdf" \
  -F "mission_id=507f1f77bcf86cd799439011" \
  -F "uploaded_by=admin@sentinelops.com" \
  -F "allowed_users=agent1@sentinelops.com,agent2@sentinelops.com"
```

#### Get Document Details
```http
GET /api/docsage/documents/{doc_id}?user_email=user@example.com
```

**Response:**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "name": "mission_briefing.pdf",
  "status": "processed",
  "uploaded_by": "admin@sentinelops.com",
  "uploaded_at": "2024-01-15T10:30:00",
  "mission_id": "mission123",
  "allowed_users": ["admin@sentinelops.com", "agent@sentinelops.com"],
  "summary": {
    "short_summary": "Mission briefing for Operation Phoenix",
    "long_summary": "Detailed mission objectives...",
    "keywords": ["mission", "phoenix", "operations"],
    "tag_suggestions": ["classified", "operations", "briefing"]
  },
  "insights": {
    "total_pages": 0,
    "word_count": 1234,
    "estimated_read_time": 6,
    "document_type": "briefing",
    "key_entities": ["Team Alpha", "Location X", "Operation Phoenix"],
    "important_sections": ["Objectives", "Timeline", "Resources"]
  },
  "extracted_text": "Full document text...",
  "file_size": 2048576,
  "mime_type": "application/pdf"
}
```

#### Get All Documents
```http
GET /api/docsage/documents?user_email=user@example.com&mission_id=mission123
```

#### Check Document Access
```http
POST /api/docsage/documents/{doc_id}/check-access
Content-Type: application/json

{
  "document_id": "doc123",
  "user_email": "agent@sentinelops.com"
}
```

#### Delete Document
```http
DELETE /api/docsage/documents/{doc_id}
```

### Document Search

#### Search Documents
```http
GET /api/docsage/search?q=mission+briefing&user_email=user@example.com
```

**Response:**
```json
{
  "query": "mission briefing",
  "total_results": 3,
  "results": [
    {
      "id": "doc123",
      "name": "mission_briefing.pdf",
      "summary": "Mission briefing for Operation Phoenix",
      "keywords": ["mission", "briefing"],
      "uploaded_by": "admin@sentinelops.com",
      "uploaded_at": "2024-01-15T10:30:00",
      "match_context": "...this mission briefing contains..."
    }
  ]
}
```

### AI Chat

#### Ask Question About Document
```http
POST /api/docsage/chat?user_email=admin@sentinelops.com
Content-Type: application/json

{
  "document_id": "507f1f77bcf86cd799439011",
  "question": "What are the main objectives of this mission?",
  "include_history": true
}
```

**Response:**
```json
{
  "answer": "The main objectives of this mission are: 1) Secure the area, 2) Retrieve the artifact, 3) Return safely to base.",
  "sources": ["mission_briefing.pdf"],
  "timestamp": "2024-01-15T11:00:00"
}
```

#### Get Chat History
```http
GET /api/docsage/chat/history/{document_id}?user_email=admin@sentinelops.com
```

**Response:**
```json
{
  "document_id": "doc123",
  "mission_id": "mission123",
  "user_id": "admin@sentinelops.com",
  "messages": [
    {
      "role": "user",
      "content": "What are the objectives?",
      "timestamp": "2024-01-15T10:30:00"
    },
    {
      "role": "assistant",
      "content": "The main objectives are...",
      "timestamp": "2024-01-15T10:30:01"
    }
  ],
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:01"
}
```

## 📊 Data Models

### Document
```python
{
    "name": str,                    # Filename
    "file_path": str,               # Storage path
    "file_size": int,               # Size in bytes
    "mime_type": str,               # MIME type
    "status": str,                  # uploaded/processing/processed/error
    "uploaded_by": str,             # Uploader email
    "uploaded_at": datetime,        # Upload timestamp
    "mission_id": str,              # Associated mission (optional)
    "allowed_users": [str],         # User emails with access
    "extracted_text": str,          # Extracted text
    "summary": {
        "short_summary": str,
        "long_summary": str,
        "keywords": [str],
        "tag_suggestions": [str]
    },
    "insights": {
        "word_count": int,
        "estimated_read_time": int,
        "document_type": str,
        "key_entities": [str],
        "important_sections": [str]
    },
    "processed_at": datetime
}
```

### Chat History
```python
{
    "document_id": str,
    "mission_id": str,
    "user_id": str,
    "messages": [
        {
            "role": str,            # user/assistant
            "content": str,
            "timestamp": datetime
        }
    ],
    "created_at": datetime,
    "updated_at": datetime
}
```

## 🔐 Access Control Logic

1. **Uploader**: Always has full access to documents they uploaded
2. **Allowed Users**: Users in the `allowed_users` list have access
3. **Mission-Based**: Only admin and assigned agents can view mission documents
4. **Public Documents**: Documents with empty `allowed_users` list are public

## 🚀 Usage Flow

### For Admin:

1. **Create Mission** (via Mission Ops)
2. **Assign Agent** to mission
3. **Upload Documents**:
   - Select files
   - Link to mission
   - System automatically adds admin and assigned agent to allowed_users
4. **View Documents**:
   - See page-level summaries
   - View tag suggestions
   - Check document insights
5. **Chat with Document**:
   - Ask questions about content
   - Get AI-powered answers
   - View chat history

### For Assigned Agent:

1. **View Mission Documents**:
   - Filter documents by mission
   - Only see documents from assigned missions
2. **Review Insights**:
   - Page-level summary
   - Tag suggestions
   - Document insights (word count, read time, etc.)
3. **Chat with Documents**:
   - Ask questions to understand content quickly
   - Save time by getting AI summaries instead of reading entire document
4. **View Full Document**: Access complete text if needed

## 🧪 Testing

### Test Document Upload
```python
import requests

files = {'file': open('test.pdf', 'rb')}
data = {
    'mission_id': 'mission123',
    'uploaded_by': 'admin@sentinelops.com',
    'allowed_users': 'agent1@sentinelops.com'
}

response = requests.post(
    'http://localhost:8000/api/docsage/upload',
    files=files,
    data=data
)
print(response.json())
```

### Test Chat
```python
import requests

payload = {
    "document_id": "doc123",
    "question": "What is this document about?",
    "include_history": True
}

response = requests.post(
    'http://localhost:8000/api/docsage/chat?user_email=admin@sentinelops.com',
    json=payload
)
print(response.json())
```

## 📝 File Structure

```
doc_sage/
├── __init__.py
├── models.py              # Pydantic models
├── routes.py              # API endpoints
├── services.py            # Business logic
├── ai_processor.py        # AI processing with Ollama
├── text_extractor.py      # Text extraction from files
├── utils.py               # Utility functions
└── README.md              # This file
```

## 🔮 Future Enhancements

- [ ] Page-by-page summaries for PDFs
- [ ] Support for more file formats (DOCX, XLSX)
- [ ] Batch document upload
- [ ] Document comparison feature
- [ ] Advanced search with filters
- [ ] Document versioning
- [ ] Collaborative annotations
- [ ] Export chat history as report

## 🐛 Troubleshooting

### Document Processing Stuck
- Check if AI processor is initialized
- Verify Ollama is running (ollama serve)
- Check MongoDB connection

### Access Denied Errors
- Verify user email in allowed_users
- Check if user is admin or assigned agent
- Ensure mission assignment is correct

### Chat Not Working
- Confirm document status is "processed"
- Check if extracted_text exists
- Verify user has document access

## 📚 Dependencies

- **FastAPI**: Web framework
- **MongoDB**: Document storage
- **Ollama**: Local LLM (llama3.2:3b) for AI processing
- **Tesseract OCR**: Image text extraction
- **PyPDF2**: PDF text extraction
- **Pillow**: Image processing

## 🎓 Best Practices

1. Always link documents to missions for better organization
2. Set appropriate allowed_users for sensitive documents
3. Use chat feature to quickly understand document content
4. Regularly clean up old/unused documents
5. Monitor document processing status
6. Use tag suggestions for better categorization

---

**Version**: 2.0  
**Last Updated**: December 8, 2025  
**Maintained by**: SentinelOps Development Team
