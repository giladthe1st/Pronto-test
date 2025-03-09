"""
Enhanced image handling utility for the Pronto application.
Provides efficient caching and display of images from Google Drive URLs.
"""
import os
import hashlib
import requests
from io import BytesIO
from PIL import Image, ImageDraw
import re
import base64
from functools import lru_cache
import traceback

# Import Google Drive utilities
from utils.drive_utils import get_file_id_from_drive_url, download_with_credentials, DEFAULT_LOGO_SIZE

# Constants for image handling
CACHE_DIR = "logo_cache"

def ensure_directories_exist():
    """Ensure all required directories exist"""
    directories = ["data", "flyers", "cached_images", "logo_images", CACHE_DIR]
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")

def ensure_cache_directory():
    """Ensure the image cache directory exists"""
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)
        print(f"Created image cache directory: {CACHE_DIR}")

def clean_cache_directory():
    """Remove duplicate images from cache directory (same hash with different extensions)"""
    import glob
    
    # Get all cached files
    cache_files = glob.glob("cached_images/*.*")
    
    # Group by filename without extension
    file_groups = {}
    for file_path in cache_files:
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        if base_name not in file_groups:
            file_groups[base_name] = []
        file_groups[base_name].append(file_path)
    
    # Remove duplicates (keep PNG, remove JPG if both exist)
    for base_name, files in file_groups.items():
        if len(files) > 1:
            # Sort to prioritize PNG files (keep them, remove others)
            files.sort(key=lambda x: 0 if x.lower().endswith('.png') else 1)
            # Keep the first file (PNG), remove others
            for file_to_remove in files[1:]:
                try:
                    os.remove(file_to_remove)
                    print(f"Removed duplicate cache file: {file_to_remove}")
                except Exception as e:
                    print(f"Error removing {file_to_remove}: {e}")

def create_empty_box(size=(80, 80)):
    """Create a simple empty box for missing images"""
    width, height = size
    # Create a blank white image with a light gray border
    img = Image.new('RGB', (width, height), color=(255, 255, 255))
    
    # Draw a light gray border (by filling the image with gray, then a smaller white rectangle)
    draw = ImageDraw.Draw(img)
    
    # Draw border (1px)
    border_color = (220, 220, 220)
    draw.rectangle([(0, 0), (width-1, height-1)], outline=border_color)
    
    return img

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

def get_image_from_url(url, size=DEFAULT_LOGO_SIZE):
    """
    Download an image from a URL and resize it.
    
    Args:
        url (str): URL of the image
        size (tuple): Target size for the image
        
    Returns:
        PIL.Image or None: Processed image or None if failed
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        img = Image.open(BytesIO(response.content))
        
        # Convert RGBA to RGB if needed
        if img.mode == 'RGBA':
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])
            img = background
        
        # Resize while maintaining aspect ratio
        img.thumbnail(size, Image.LANCZOS)
        
        return img
    except Exception as e:
        print(f"Error downloading image from URL {url}: {e}")
        return None

def get_logo_from_drive(url, restaurant_name, size=DEFAULT_LOGO_SIZE, force_refresh=False):
    """
    Get a logo image from Google Drive, with caching.
    
    Args:
        url (str): Google Drive URL
        restaurant_name (str): Name of the restaurant
        size (tuple): Target size for the image
        force_refresh (bool): Whether to force a refresh from the source
        
    Returns:
        PIL.Image: Logo image or placeholder if not found
    """
    # Check if URL is valid
    if not url or not isinstance(url, str) or not url.strip():
        print(f"Invalid URL for {restaurant_name}: {url}")
        return create_placeholder_image(size)
    
    # Generate cache path
    cache_path = get_cache_path(url, restaurant_name)
    
    # Check if cached version exists and we're not forcing a refresh
    if os.path.exists(cache_path) and not force_refresh:
        try:
            # Load from cache
            img = Image.open(cache_path)
            # Resize if needed
            if img.size != size:
                img.thumbnail(size, Image.LANCZOS)
            return img
        except Exception as e:
            print(f"Error loading cached image for {restaurant_name}: {e}")
            # If there's an error loading the cached image, we'll try to download it again
    
    # Extract file ID from Google Drive URL
    file_id = get_file_id_from_drive_url(url)
    
    if not file_id:
        print(f"Could not extract file ID from URL: {url}")
        return create_placeholder_image(size)
    
    # Try to download using Google Drive API with credentials
    img = download_with_credentials(file_id, cache_path, size)
    
    if img:
        return img
    
    # If all methods fail, return a placeholder image
    return create_placeholder_image(size)

@lru_cache(maxsize=100)
def get_image_base64(img):
    """
    Convert a PIL image to base64 for embedding in HTML.
    
    Args:
        img (PIL.Image): Image to convert
        
    Returns:
        str: Base64 encoded image
    """
    if not img:
        return None
    
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def display_logo(url, restaurant_name, size=DEFAULT_LOGO_SIZE, force_refresh=False):
    """
    Display a logo image from Google Drive in Streamlit.
    
    Args:
        url (str): Google Drive URL
        restaurant_name (str): Name of the restaurant
        size (tuple): Target size for the image
        force_refresh (bool): Whether to force a refresh from the source
        
    Returns:
        str: HTML for displaying the image
    """
    try:
        # Get the logo image
        img = get_logo_from_drive(url, restaurant_name, size, force_refresh)
        
        # Convert to base64
        img_base64 = get_image_base64(img)
        
        # Create HTML for displaying the image
        html = f'<img src="data:image/png;base64,{img_base64}" width="{size[0]}" height="{size[1]}" style="object-fit: contain;">'
        
        return html
    except Exception as e:
        print(f"Error displaying logo for {restaurant_name}: {e}")
        traceback.print_exc()
        return f'<div style="width:{size[0]}px;height:{size[1]}px;border:1px solid #ddd;display:flex;align-items:center;justify-content:center;color:#999;">Logo</div>'
