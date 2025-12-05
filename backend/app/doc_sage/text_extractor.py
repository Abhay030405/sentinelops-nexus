"""
Text Extraction Module
Handles extraction from PDF, images, and text files
"""

import logging
import os
from pathlib import Path
from typing import Tuple
import pytesseract
from PIL import Image
import PyPDF2

logger = logging.getLogger(__name__)


async def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF file"""
    try:
        text = ""
        with open(file_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            num_pages = len(pdf_reader.pages)
            
            logger.info(f"📄 Extracting text from PDF with {num_pages} pages")
            
            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                text += page.extract_text()
                text += f"\n\n--- Page {page_num + 1} ---\n\n"
        
        logger.info(f"✅ Extracted {len(text)} characters from PDF")
        return text
    except Exception as e:
        logger.error(f"❌ Error extracting PDF: {e}")
        raise


async def extract_text_from_image(file_path: str) -> str:
    """Extract text from image using OCR (Tesseract)"""
    try:
        image = Image.open(file_path)
        
        # Optimize image for OCR
        image = image.convert('RGB')
        
        logger.info("🔍 Running OCR on image")
        text = pytesseract.image_to_string(image)
        
        logger.info(f"✅ Extracted {len(text)} characters from image")
        return text
    except Exception as e:
        logger.error(f"❌ Error extracting from image: {e}")
        raise


async def extract_text_from_txt(file_path: str) -> str:
    """Extract text from text file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as txt_file:
            text = txt_file.read()
        
        logger.info(f"✅ Extracted {len(text)} characters from text file")
        return text
    except Exception as e:
        logger.error(f"❌ Error extracting from text file: {e}")
        raise


async def extract_text(file_path: str, mime_type: str) -> str:
    """
    Extract text based on file type
    
    Args:
        file_path: Path to the file
        mime_type: MIME type of the file
    
    Returns:
        Extracted text content
    """
    logger.info(f"🔄 Extracting text from {mime_type} file")
    
    if mime_type == 'application/pdf':
        return await extract_text_from_pdf(file_path)
    elif mime_type in ['image/jpeg', 'image/png', 'image/jpg', 'image/tiff']:
        return await extract_text_from_image(file_path)
    elif mime_type == 'text/plain':
        return await extract_text_from_txt(file_path)
    else:
        raise ValueError(f"Unsupported file type: {mime_type}")
