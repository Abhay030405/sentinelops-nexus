import google.generativeai as genai
from app.config.settings import settings
import json

class GeminiClient:
    def __init__(self):
        if not settings.GEMINI_API_KEY:
            print("⚠️  Warning: GEMINI_API_KEY not set in .env file")
        else:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
            print("✅ Gemini AI initialized successfully!")

    async def generate_summary(self, text: str) -> dict:
        """Generate short and long summary of the text"""
        try:
            # Short Summary
            short_prompt = f"""
            Summarize the following document in 1-2 sentences:
            
            {text[:3000]}  
            
            Provide only the summary, no extra text.
            """
            
            short_response = self.model.generate_content(short_prompt)
            short_summary = short_response.text.strip()

            # Long Summary
            long_prompt = f"""
            Provide a detailed summary of the following document in 3-5 paragraphs:
            
            {text[:5000]}
            
            Provide only the summary, no extra text.
            """
            
            long_response = self.model.generate_content(long_prompt)
            long_summary = long_response.text.strip()

            return {
                "short_summary": short_summary,
                "long_summary": long_summary
            }
        except Exception as e:
            print(f"❌ Error generating summary: {str(e)}")
            return {
                "short_summary": "Summary generation failed",
                "long_summary": "Summary generation failed"
            }

    async def extract_keywords(self, text: str) -> list:
        """Extract important keywords from the text"""
        try:
            prompt = f"""
            Extract 5-10 important keywords or key phrases from the following text.
            Return ONLY a JSON array of strings, nothing else.
            
            Example format: ["keyword1", "keyword2", "keyword3"]
            
            Text:
            {text[:3000]}
            """
            
            response = self.model.generate_content(prompt)
            keywords_text = response.text.strip()
            
            # Try to parse JSON
            try:
                # Remove markdown code blocks if present
                if "```" in keywords_text:
                    keywords_text = keywords_text.split("```")[1]
                    if keywords_text.startswith("json"):
                        keywords_text = keywords_text[4:]
                keywords_text = keywords_text.strip()
                
                keywords = json.loads(keywords_text)
                return keywords[:10]  # Limit to 10 keywords
            except:
                # Fallback: extract words manually
                words = keywords_text.replace("[", "").replace("]", "").replace('"', "")
                keywords = [w.strip() for w in words.split(",")]
                return keywords[:10]
                
        except Exception as e:
            print(f"❌ Error extracting keywords: {str(e)}")
            return []

gemini_client = GeminiClient()