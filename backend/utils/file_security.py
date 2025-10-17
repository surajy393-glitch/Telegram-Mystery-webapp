"""
File Upload Security Utilities
Sanitization and validation for file uploads
"""
import os
import secrets
import mimetypes
from pathlib import Path
from typing import Tuple, Optional

# Allowed file extensions
ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.heic'}
ALLOWED_MIME_TYPES = {
    'image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/heic'
}

# Maximum file sizes (in bytes)
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_VIDEO_SIZE = 50 * 1024 * 1024  # 50MB


def generate_secure_filename(original_filename: str, user_id: str) -> str:
    """
    Generate a secure random filename preserving only the extension
    
    Args:
        original_filename: Original uploaded filename
        user_id: User ID for additional uniqueness
        
    Returns:
        Secure randomized filename
    """
    # Extract extension safely
    ext = Path(original_filename).suffix.lower()
    
    # Validate extension
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValueError(f"File extension {ext} not allowed")
    
    # Generate random filename
    random_name = secrets.token_urlsafe(16)
    return f"{user_id}_{random_name}{ext}"


def validate_image_file(file_content: bytes, filename: str) -> Tuple[bool, Optional[str]]:
    """
    Validate image file by checking MIME type and magic bytes
    
    Args:
        file_content: File content bytes
        filename: Original filename
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check file size
    if len(file_content) > MAX_IMAGE_SIZE:
        return False, f"File size exceeds {MAX_IMAGE_SIZE // (1024*1024)}MB limit"
    
    # Check extension
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        return False, f"File type {ext} not allowed. Allowed: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}"
    
    # Check magic bytes (first few bytes identify file type)
    if not file_content:
        return False, "Empty file"
    
    # JPEG magic bytes
    if file_content[:2] == b'\xff\xd8':
        return True, None
    
    # PNG magic bytes
    if file_content[:8] == b'\x89PNG\r\n\x1a\n':
        return True, None
    
    # GIF magic bytes
    if file_content[:6] in (b'GIF87a', b'GIF89a'):
        return True, None
    
    # WEBP magic bytes
    if file_content[:4] == b'RIFF' and file_content[8:12] == b'WEBP':
        return True, None
    
    return False, "File content does not match expected image format"


def sanitize_path(path: str, base_dir: str) -> str:
    """
    Prevent directory traversal attacks
    
    Args:
        path: Requested file path
        base_dir: Base directory for uploads
        
    Returns:
        Sanitized absolute path
        
    Raises:
        ValueError: If path tries to escape base directory
    """
    # Resolve to absolute path
    base_path = Path(base_dir).resolve()
    requested_path = (base_path / path).resolve()
    
    # Check if requested path is within base directory
    try:
        requested_path.relative_to(base_path)
    except ValueError:
        raise ValueError("Invalid file path: directory traversal detected")
    
    return str(requested_path)


def clean_filename(filename: str) -> str:
    """
    Remove dangerous characters from filename
    
    Args:
        filename: Original filename
        
    Returns:
        Cleaned filename
    """
    # Remove path separators and dangerous characters
    dangerous_chars = ['/', '\\', '..', '\x00', '\n', '\r']
    clean_name = filename
    
    for char in dangerous_chars:
        clean_name = clean_name.replace(char, '')
    
    # Limit length
    if len(clean_name) > 255:
        ext = Path(clean_name).suffix
        clean_name = clean_name[:255-len(ext)] + ext
    
    return clean_name
