"""
Utility functions for Identity Vault
QR token generation, password hashing, etc.
"""

import secrets
import qrcode
import io
import base64
from passlib.context import CryptContext
from app.config.settings import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_qr_token(length: int = None) -> str:
    """
    Generate a secure random QR token
    
    Args:
        length: Token length (default from settings)
        
    Returns:
        Hex string token
    """
    if length is None:
        length = settings.QR_TOKEN_LENGTH
    return secrets.token_hex(length)


def generate_qr_code_image(data: str) -> str:
    """
    Generate QR code image from data
    
    Args:
        data: String data to encode in QR
        
    Returns:
        Base64 encoded PNG image
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash
    
    Args:
        plain_password: Plain text password
        hashed_password: Bcrypt hashed password
        
    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_qr_token_data(username: str, qr_token: str) -> str:
    """
    Create QR code data string for user authentication
    
    Args:
        username: User's username
        qr_token: User's unique QR token
        
    Returns:
        Formatted string for QR code
    """
    return f"SENTINEL_OPS::{username}::{qr_token}"