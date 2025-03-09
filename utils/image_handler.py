"""
Enhanced image handling utility for the Pronto application.
Provides efficient display of images from the static directory.
"""
import os
import hashlib
from io import BytesIO
from PIL import Image, ImageDraw
import re
import base64
from functools import lru_cache
import traceback

# Import Google Drive utilities with fallback
try:
    from utils.drive_utils import (
        get_file_id_from_drive_url, 
        download_with_credentials, 
        DEFAULT_LOGO_SIZE,
        GOOGLE_DRIVE_API_AVAILABLE
    )
except ImportError:
    # Define fallbacks if drive_utils is not available
    print("Warning: drive_utils module not available. Using fallback values.")
    DEFAULT_LOGO_SIZE = (140, 140)
    GOOGLE_DRIVE_API_AVAILABLE = False
    
    def get_file_id_from_drive_url(url):
        """Fallback implementation"""
        return None
        
    def download_with_credentials(file_id, cache_path, size=DEFAULT_LOGO_SIZE):
        """Fallback implementation"""
        return None

# Constants for image handling
CACHE_DIR = "logo_cache"
STATIC_LOGOS_DIR = "static/logos"

def ensure_directories_exist():
    """Ensure all required directories exist"""
    directories = ["data", "flyers", "cached_images", "logo_images", CACHE_DIR, STATIC_LOGOS_DIR]
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")

def ensure_cache_directory():
    """Ensure the image cache directory exists"""
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)
        print(f"Created image cache directory: {CACHE_DIR}")

def ensure_static_directory():
    """Ensure the static logos directory exists"""
    if not os.path.exists(STATIC_LOGOS_DIR):
        os.makedirs(STATIC_LOGOS_DIR)
        print(f"Created static logos directory: {STATIC_LOGOS_DIR}")

def create_safe_filename(name):
    """
    Create a safe filename from a restaurant name or other string.
    
    Args:
        name (str): Input string
        
    Returns:
        str: Safe filename string
    """
    if not name:
        return "unknown"
    return re.sub(r'[^\w\-_]', '_', name.lower())

def get_cache_path(url, restaurant_name):
    """
    Generate a cache path for an image based on URL and restaurant name.
    
    Args:
        url (str): Image URL
        restaurant_name (str): Name of the restaurant
        
    Returns:
        str: Path to the cached image
    """
    # Create a unique hash based on the URL
    url_hash = hashlib.md5(url.encode()).hexdigest()[:10]
    safe_name = create_safe_filename(restaurant_name)
    return os.path.join(CACHE_DIR, f"{safe_name}_{url_hash}.png")

def get_static_path(url, restaurant_name):
    """
    Generate a path for an image in the static directory based on URL and restaurant name.
    
    Args:
        url (str): Image URL
        restaurant_name (str): Name of the restaurant
        
    Returns:
        str: Path to the static image
    """
    # Try to extract the file ID from the URL for consistency with the download script
    file_id = None
    try:
        # Pattern 1: https://drive.google.com/file/d/{file_id}/view
        if '/file/d/' in url:
            file_id = url.split('/file/d/')[1].split('/')[0]
        # Pattern 2: https://drive.google.com/open?id={file_id}
        elif 'open?id=' in url:
            file_id = url.split('open?id=')[1].split('&')[0]
        # Pattern 3: https://drive.google.com/uc?id={file_id}
        elif 'uc?id=' in url:
            file_id = url.split('uc?id=')[1].split('&')[0]
    except IndexError as e:
        # If extraction fails, fall back to hash method
        print(f"Could not extract file ID from URL: {url}, error: {e}")
        pass
    
    # If we got a file ID, use it for the filename
    if file_id:
        safe_name = create_safe_filename(restaurant_name)
        return os.path.join(STATIC_LOGOS_DIR, f"{safe_name}_{file_id[:10]}.png")
    
    # Fallback to hash method if file ID extraction failed
    url_hash = hashlib.md5(url.encode()).hexdigest()[:10]
    safe_name = create_safe_filename(restaurant_name)
    return os.path.join(STATIC_LOGOS_DIR, f"{safe_name}_{url_hash}.png")

def create_placeholder_image(size=DEFAULT_LOGO_SIZE, text=None):
    """
    Create a placeholder image for missing logos.
    
    Args:
        size (tuple): Width and height of the image
        text (str): Optional text to display on the image
        
    Returns:
        PIL.Image: Placeholder image
    """
    width, height = size
    # Create a blank white image with a light gray border
    img = Image.new('RGB', (width, height), color=(255, 255, 255))
    
    # Draw a light gray border
    draw = ImageDraw.Draw(img)
    border_color = (220, 220, 220)
    draw.rectangle([(0, 0), (width-1, height-1)], outline=border_color)
    
    # Add text if provided
    if text:
        # This is a simplified text drawing - in a real app, you'd want to use
        # proper font handling and text wrapping
        draw.text((width//2-15, height//2-5), text, fill=(150, 150, 150))
    
    return img

def get_logo(url, restaurant_name, size=DEFAULT_LOGO_SIZE):
    """
    Get a logo image from the static directory or create a placeholder.
    
    Args:
        url (str): Google Drive URL (used for generating the filename)
        restaurant_name (str): Name of the restaurant
        size (tuple): Target size for the image
        
    Returns:
        PIL.Image: Logo image or placeholder if not found
    """
    # Check if URL is valid
    if not url or not isinstance(url, str) or not url.strip():
        print(f"Invalid URL for {restaurant_name}: {url}")
        return create_placeholder_image(size)
    
    # Generate static path
    static_path = get_static_path(url, restaurant_name)
    
    # Check if image exists in static directory
    if os.path.exists(static_path):
        try:
            # Load from static directory
            img = Image.open(static_path)
            # Resize if needed
            if img.size != size:
                img.thumbnail(size, Image.LANCZOS)
            print(f"Using static image for {restaurant_name} from {static_path}")
            return img
        except Exception as e:
            print(f"Error loading static image for {restaurant_name}: {e}")
            # If there's an error loading the static image, use placeholder
    
    # If static image doesn't exist or failed to load, return a placeholder
    print(f"No static image found for {restaurant_name}")
    return create_placeholder_image(size)

@lru_cache(maxsize=100)
def get_image_base64(img_path):
    """
    Convert an image file to base64 for embedding in HTML.
    
    Args:
        img_path (str): Path to the image file
        
    Returns:
        str: Base64 encoded image
    """
    if not img_path or not os.path.exists(img_path):
        return None
    
    try:
        with open(img_path, 'rb') as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception as e:
        print(f"Error encoding image to base64: {e}")
        return None

def display_logo(url, restaurant_name, size=DEFAULT_LOGO_SIZE):
    """
    Display a logo image from the static directory.
    
    Args:
        url (str): Google Drive URL (used for generating the filename)
        restaurant_name (str): Name of the restaurant
        size (tuple): Target size for the image
        
    Returns:
        str: HTML for displaying the image
    """
    try:
        # Generate static path
        static_path = get_static_path(url, restaurant_name)
        
        # Check if image exists in static directory
        if os.path.exists(static_path):
            img_base64 = get_image_base64(static_path)
            if img_base64:
                html = f'<img src="data:image/png;base64,{img_base64}" width="{size[0]}" height="{size[1]}" style="object-fit: contain;">'
                return html
        
        # If static image doesn't exist or failed to encode, get a placeholder image
        img = get_logo(url, restaurant_name, size)
        
        # Convert the image directly
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        html = f'<img src="data:image/png;base64,{img_base64}" width="{size[0]}" height="{size[1]}" style="object-fit: contain;">'
        return html
        
    except Exception as e:
        print(f"Error displaying logo for {restaurant_name}: {e}")
        traceback.print_exc()
        return f'<div style="width:{size[0]}px;height:{size[1]}px;border:1px solid #ddd;display:flex;align-items:center;justify-content:center;color:#999;">Logo</div>'
