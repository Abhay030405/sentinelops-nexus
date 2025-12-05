"""
AI Processor Module
Handles AI-powered summarization and keyword extraction using Gemini
"""

import logging
from typing import Tuple, List
import google.generativeai as genai
from app.config.settings import settings

logger = logging.getLogger(__name__)


class AIProcessor:
    """Process documents with AI for summarization and keyword extraction"""
    
    def __init__(self):
        """Initialize AI processor with Gemini"""
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not set in environment")
        
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
        logger.info(f"✅ Initialized AI Processor with {settings.GEMINI_MODEL}")
    
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
            
            short_response = self.model.generate_content(short_prompt)
            short_summary = short_response.text.strip()
            
            # Long summary
            long_prompt = f"""Provide a comprehensive detailed summary of the following text. 
Include main points, important details, and key concepts.
Limit to 500 words maximum.

Text:
{text}

Comprehensive Summary:"""
            
            long_response = self.model.generate_content(long_prompt)
            long_summary = long_response.text.strip()
            
            logger.info("✅ Generated summaries successfully")
            return short_summary, long_summary
        
        except Exception as e:
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
            
            response = self.model.generate_content(keyword_prompt)
            keywords_str = response.text
            
            # Parse keywords from comma-separated string
            keywords = [kw.strip().lower() for kw in keywords_str.split(',')]
            keywords = [kw for kw in keywords if kw]  # Remove empty strings
            keywords = keywords[:num_keywords]  # Limit to requested number
            
            logger.info(f"✅ Extracted {len(keywords)} keywords")
            return keywords
        
        except Exception as e:
            logger.error(f"❌ Error extracting keywords: {e}")
            raise
    
    def process_document(self, text: str) -> dict:
        """
        Complete document processing: summary + keywords
        
        Args:
            text: Extracted document text
        
        Returns:
            Dictionary with summaries and keywords
        """
        try:
            logger.info("⚙️ Starting document AI processing")
            
            short_summary, long_summary = self.summarize_text(text)
            keywords = self.extract_keywords(text)
            
            result = {
                "short_summary": short_summary,
                "long_summary": long_summary,
                "keywords": keywords
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

