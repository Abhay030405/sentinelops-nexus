"""
AI Processor Module
Handles AI-powered summarization and keyword extraction using Ollama
"""

import logging
from typing import Tuple, List
import requests
import json
from app.config.settings import settings

logger = logging.getLogger(__name__)


class AIProcessor:
    """Process documents with AI for summarization and keyword extraction"""
    
    def __init__(self):
        """Initialize AI processor with Ollama"""
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL
        # Test connection
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                logger.info(f"✅ Initialized AI Processor with Ollama ({self.model})")
            else:
                raise ConnectionError("Cannot connect to Ollama")
        except Exception as e:
            logger.error(f"❌ Ollama not running. Start it with: ollama serve")
            raise ConnectionError(f"Ollama connection failed: {e}")
    
    def _call_ollama(self, prompt: str, max_tokens: int = 500) -> str:
        """Call Ollama API"""
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": max_tokens,
                        "temperature": 0.7
                    }
                },
                timeout=60
            )
            response.raise_for_status()
            return response.json()["response"].strip()
        except Exception as e:
            logger.error(f"❌ Ollama API error: {e}")
            raise
    
    def _generate(self, prompt: str, max_tokens: int = 500) -> str:
        """Generate text using Ollama"""
        return self._call_ollama(prompt, max_tokens)
    
    def summarize_text(self, text: str, max_length: int = 200) -> Tuple[str, str]:
        """
        Generate both short and long summaries
        
        Args:
            text: Text to summarize
            max_length: Max length for short summary
        
        Returns:
            Tuple of (short_summary, long_summary)
        """
        try:
            text = text.strip()
            if len(text) > 10000:
                text = text[:10000]
            
            logger.info(f"🤖 Generating summaries for {len(text)} characters")
            
            # Short summary
            short_prompt = f"""Provide a concise summary in {max_length} words or less. 
Be specific and highlight key information.

Text:
{text}

Summary:"""
            
            short_summary = self._generate(short_prompt, max_tokens=200)
            
            # Long summary
            long_prompt = f"""Provide a comprehensive detailed summary of the following text. 
Include main points, important details, and key concepts.
Limit to 500 words maximum.

Text:
{text}

Comprehensive Summary:"""
            
            long_summary = self._generate(long_prompt, max_tokens=500)
            
            logger.info("✅ Generated summaries successfully")
            return short_summary, long_summary
        
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "quota" in error_str.lower():
                logger.warning(f"⚠️ API quota exceeded. Using fallback summary.")
                # Generate basic fallback summary
                words = text.split()
                short_summary = " ".join(words[:50]) + "..." if len(words) > 50 else text
                long_summary = " ".join(words[:200]) + "..." if len(words) > 200 else text
                return short_summary, long_summary
            logger.error(f"❌ Error generating summaries: {e}")
            raise
    
    def extract_keywords(self, text: str, num_keywords: int = 10) -> List[str]:
        """
        Extract important keywords from text
        
        Args:
            text: Text to extract keywords from
            num_keywords: Number of keywords to extract
        
        Returns:
            List of extracted keywords
        """
        try:
            text = text.strip()
            if len(text) > 5000:
                text = text[:5000]
            
            logger.info(f"🔑 Extracting keywords from {len(text)} characters")
            
            keyword_prompt = f"""Extract the top {num_keywords} most important keywords from the following text.
Return only the keywords separated by commas, without numbering or explanations.

Text:
{text}

Keywords:"""
            
            keywords_str = self._generate(keyword_prompt, max_tokens=100)
            
            # Parse keywords from comma-separated string
            keywords = [kw.strip().lower() for kw in keywords_str.split(',')]
            keywords = [kw for kw in keywords if kw]  # Remove empty strings
            keywords = keywords[:num_keywords]  # Limit to requested number
            
            logger.info(f"✅ Extracted {len(keywords)} keywords")
            return keywords
        
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "quota" in error_str.lower():
                logger.warning(f"⚠️ API quota exceeded. Using fallback keyword extraction.")
                # Simple keyword extraction - most common words
                words = text.lower().split()
                # Remove common stop words
                stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'is', 'was', 'are', 'be', 'been', 'being'}
                keywords = [w for w in words if w not in stop_words and len(w) > 3]
                # Get unique keywords
                unique_keywords = list(dict.fromkeys(keywords))[:num_keywords]
                return unique_keywords
            logger.error(f"❌ Error extracting keywords: {e}")
            raise
    
    def generate_tag_suggestions(self, text: str, keywords: List[str]) -> List[str]:
        """
        Generate tag suggestions based on document content
        
        Args:
            text: Document text
            keywords: Extracted keywords
        
        Returns:
            List of suggested tags
        """
        try:
            logger.info("🏷️ Generating tag suggestions")
            
            tag_prompt = f"""Based on the following document content and keywords, suggest 5-7 relevant tags for categorization.
Tags should be single words or short phrases that help categorize and find this document.

Keywords: {', '.join(keywords)}

Text sample: {text[:1000]}

Return only the tags separated by commas:"""
            
            tags_str = self._generate(tag_prompt, max_tokens=100)
            
            tags = [tag.strip().lower() for tag in tags_str.split(',')]
            tags = [tag for tag in tags if tag][:7]
            
            logger.info(f"✅ Generated {len(tags)} tag suggestions")
            return tags
        
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "quota" in error_str.lower():
                logger.warning(f"⚠️ API quota exceeded. Using keywords as tags.")
                return keywords[:7]
            logger.error(f"❌ Error generating tags: {e}")
            return keywords[:5] if keywords else []
    
    def generate_document_insights(self, text: str) -> dict:
        """
        Generate comprehensive document insights
        
        Args:
            text: Document text
        
        Returns:
            Dictionary with document insights
        """
        try:
            logger.info("📊 Generating document insights")
            
            words = text.split()
            word_count = len(words)
            estimated_read_time = max(1, word_count // 200)  # ~200 words per minute
            
            insight_prompt = f"""Analyze this document and provide:
1. Document type (e.g., report, manual, guide, memo, analysis)
2. Top 5 key entities mentioned (people, places, organizations, concepts)
3. Important sections or topics covered (list 3-5)

Text sample: {text[:2000]}

Format your response as:
Type: [type]
Entities: [entity1, entity2, entity3, entity4, entity5]
Sections: [section1, section2, section3]"""
            
            result_text = self._generate(insight_prompt, max_tokens=300)
            
            # Parse response
            document_type = None
            key_entities = []
            important_sections = []
            
            for line in result_text.split('\n'):
                if line.startswith('Type:'):
                    document_type = line.replace('Type:', '').strip()
                elif line.startswith('Entities:'):
                    entities_str = line.replace('Entities:', '').strip()
                    key_entities = [e.strip() for e in entities_str.split(',')]
                elif line.startswith('Sections:'):
                    sections_str = line.replace('Sections:', '').strip()
                    important_sections = [s.strip() for s in sections_str.split(',')]
            
            insights = {
                "word_count": word_count,
                "estimated_read_time": estimated_read_time,
                "document_type": document_type,
                "key_entities": key_entities[:5],
                "important_sections": important_sections[:5]
            }
            
            logger.info("✅ Document insights generated")
            return insights
        
        except Exception as e:
            error_str = str(e)
            words = text.split()
            word_count = len(words)
            
            if "429" in error_str or "quota" in error_str.lower():
                logger.warning(f"⚠️ API quota exceeded. Using basic insights.")
            else:
                logger.error(f"❌ Error generating insights: {e}")
            
            return {
                "word_count": word_count,
                "estimated_read_time": max(1, word_count // 200),
                "document_type": "document",
                "key_entities": [],
                "important_sections": []
            }
    
    def answer_document_question(self, question: str, document_context: str, chat_history: str = "") -> str:
        """
        Answer a question about the document
        
        Args:
            question: User's question
            document_context: Document text content
            chat_history: Previous chat messages
        
        Returns:
            AI-generated answer
        """
        try:
            logger.info(f"💬 Answering question: {question[:50]}...")
            
            prompt = f"""You are a helpful assistant analyzing a document. Answer the user's question based on the document content.
Be concise but informative. If the answer is not in the document, say so.

Document Content:
{document_context}

{f'Previous Conversation:{chat_history}' if chat_history else ''}

User Question: {question}

Answer:"""
            
            answer = self._generate(prompt, max_tokens=500)
            
            logger.info("✅ Generated answer")
            return answer
        
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "quota" in error_str.lower():
                logger.warning(f"⚠️ API quota exceeded. Cannot answer question.")
                return "I'm unable to answer questions at the moment due to API quota limits. Please try again later or view the document directly."
            logger.error(f"❌ Error answering question: {e}")
            raise
    
    def process_document(self, text: str) -> dict:
        """
        Complete document processing: summary + keywords + tags + insights
        
        Args:
            text: Extracted document text
        
        Returns:
            Dictionary with summaries, keywords, tags, and insights
        """
        try:
            logger.info("⚙️ Starting document AI processing")
            
            short_summary, long_summary = self.summarize_text(text)
            keywords = self.extract_keywords(text)
            tag_suggestions = self.generate_tag_suggestions(text, keywords)
            
            result = {
                "short_summary": short_summary,
                "long_summary": long_summary,
                "keywords": keywords,
                "tag_suggestions": tag_suggestions
            }
            
            logger.info("✅ Document AI processing completed")
            return result
        
        except Exception as e:
            logger.error(f"❌ Error processing document: {e}")
            raise


# Create singleton instance
ai_processor = None


def get_ai_processor() -> AIProcessor:
    """Get or create AI processor instance"""
    global ai_processor
    if ai_processor is None:
        ai_processor = AIProcessor()
    return ai_processor

