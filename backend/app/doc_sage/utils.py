"""
DocSage Utility Functions
Helper functions for document processing
"""

import logging

logger = logging.getLogger(__name__)


def clean_text(text: str, max_lines: int = None) -> str:
    """Clean extracted text by removing extra whitespace"""
    lines = text.split('\n')
    cleaned = '\n'.join(line.strip() for line in lines if line.strip())
    
    if max_lines:
        cleaned = '\n'.join(cleaned.split('\n')[:max_lines])
    
    return cleaned


def truncate_text(text: str, max_chars: int) -> str:
    """Truncate text to maximum characters"""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "..."
        except Exception as e:
            print(f"❌ Error extracting PDF text: {str(e)}")
            return ""

    @staticmethod
    def extract_text_from_image(file_path: str) -> str:
        """Extract text from image using OCR"""
        try:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
            return text.strip()
        except Exception as e:
            print(f"❌ Error extracting image text (OCR): {str(e)}")
            print("ℹ️  Make sure Tesseract is installed: https://github.com/tesseract-ocr/tesseract")
            return ""

    @staticmethod
    def extract_text_from_txt(file_path: str) -> str:
        """Extract text from plain text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            return text.strip()
        except Exception as e:
            print(f"❌ Error reading text file: {str(e)}")
            return ""

    @staticmethod
    def extract_text(file_path: str, file_type: str) -> str:
        """Main method to extract text based on file type"""
        file_extension = Path(file_path).suffix.lower()
        
        if file_extension == '.pdf':
            return DocumentProcessor.extract_text_from_pdf(file_path)
        elif file_extension in ['.jpg', '.jpeg', '.png']:
            return DocumentProcessor.extract_text_from_image(file_path)
        elif file_extension == '.txt':
            return DocumentProcessor.extract_text_from_txt(file_path)
        else:
            return ""

    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize extracted text"""
        # Remove excessive whitespace
        text = ' '.join(text.split())
        # Remove special characters if needed
        # text = re.sub(r'[^\w\s.,!?-]', '', text)
        return text

doc_processor = DocumentProcessor()