"""
Utility functions for image handling in the Pronto application.
"""
import os
import hashlib
import requests
from io import BytesIO
from PIL import Image, ImageDraw
import re
from google_auth import get_google_credentials

def ensure_directories_exist():
    """Ensure all required directories exist"""
    directories = ["data", "flyers", "cached_images", "logo_images"]
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)

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

def download_google_drive_image(url, restaurant_name):
    """
    Download an image from Google Drive and save it locally.
    
    Args:
        url (str): Google Drive URL
        restaurant_name (str): Name of the restaurant for the filename
        
    Returns:
        str: Path to the downloaded image or None if download failed
    """
    try:
        # URL mapping for specific restaurants with known working URLs
        url_mapping = {
            "Nicolinos": "https://drive.google.com/file/d/19xqBh-6QOZgXxdq-o2T-i5cFsqvU4PyX/view?usp=sharing"
        }
        
        # Check if we have a specific URL mapping for this restaurant
        if restaurant_name in url_mapping:
            print(f"Using mapped URL for {restaurant_name}")
            url = url_mapping[restaurant_name]
        
        # Extract the file ID from the Google Drive URL
        file_id = None
        
        # Pattern 1: https://drive.google.com/file/d/{file_id}/view
        if '/file/d/' in url:
            file_id = url.split('/file/d/')[1].split('/')[0]
        # Pattern 2: https://drive.google.com/open?id={file_id}
        elif 'open?id=' in url:
            file_id = url.split('open?id=')[1].split('&')[0]
        # Pattern 3: https://drive.google.com/uc?id={file_id}
        elif 'uc?id=' in url:
            file_id = url.split('uc?id=')[1].split('&')[0]
        
        if not file_id:
            print(f"Could not extract file ID from URL: {url}")
            return None
            
        # Create a safe filename from the restaurant name
        safe_name = re.sub(r'[^\w\-_]', '_', restaurant_name.lower())
        local_path = os.path.join("logo_images", f"{safe_name}_logo.png")
        
        # If we already have this image, just return the path
        if os.path.exists(local_path):
            return local_path
        
        # Get credentials path from environment variable or use default
        credentials_path = os.environ.get("GOOGLE_CREDENTIALS_PATH", "credentials.json")
        
        # Try to download using authenticated method first
        try:
            # Get credentials
            credentials = get_google_credentials(credentials_path)
            if credentials:
                # Create a session with the credentials
                session = requests.Session()
                access_token = credentials.get_access_token().access_token
                session.headers.update({"Authorization": f"Bearer {access_token}"})
                
                # Direct download URL format
                download_url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media"
                
                # Download the file
                response = session.get(download_url, stream=True)
                
                # Check if the request was successful
                if response.status_code == 200:
                    # Process and save the image
                    img = Image.open(BytesIO(response.content))
                    
                    # Convert RGBA to RGB if needed
                    if img.mode == 'RGBA':
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        background.paste(img, mask=img.split()[3])
                        img = background
                    
                    # Resize to a reasonable size while maintaining aspect ratio
                    img.thumbnail((200, 200), Image.LANCZOS)
                    
                    # Save the image
                    img.save(local_path, format="PNG")
                    print(f"Successfully downloaded and saved image to {local_path} using authenticated method")
                    return local_path
                else:
                    print(f"Failed to download using authenticated method. Status code: {response.status_code}")
                    print(f"Response: {response.text}")
            else:
                print("Failed to get Google credentials, falling back to unauthenticated methods")
        except Exception as e:
            print(f"Error using authenticated download method: {e}")
            
        # If authenticated method fails, fall back to previous methods
        methods = [
            # Method 1: Use the thumbnail API
            f"https://drive.google.com/thumbnail?id={file_id}&sz=w200-h200",
            # Method 2: Use the export=view parameter
            f"https://drive.google.com/uc?export=view&id={file_id}",
            # Method 3: Use the export=download parameter
            f"https://drive.google.com/uc?export=download&id={file_id}"
        ]
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        for method_url in methods:
            try:
                print(f"Trying to download image using: {method_url}")
                response = requests.get(method_url, timeout=15, headers=headers)
                
                if response.status_code == 200:
                    try:
                        img = Image.open(BytesIO(response.content))
                        
                        # Convert RGBA to RGB if needed
                        if img.mode == 'RGBA':
                            background = Image.new('RGB', img.size, (255, 255, 255))
                            background.paste(img, mask=img.split()[3])
                            img = background
                        
                        # Resize to a reasonable size while maintaining aspect ratio
                        img.thumbnail((200, 200), Image.LANCZOS)
                        
                        # Save the image
                        img.save(local_path, format="PNG")
                        print(f"Successfully downloaded and saved image to {local_path}")
                        return local_path
                    except Exception as e:
                        print(f"Error processing image from {method_url}: {e}")
                        continue
                else:
                    print(f"Failed to download from {method_url}, status code: {response.status_code}")
            except Exception as e:
                print(f"Error downloading from {method_url}: {e}")
        
        # If all methods failed, return None
        print(f"All download methods failed for URL: {url}")
        return None
        
    except Exception as e:
        print(f"Error in download_google_drive_image: {e}")
        return None

def load_image_from_url(url_or_path, restaurant_name=None):
    """Load an image from a URL or local file path with local caching."""
    try:
        # For Google Drive links, try to download and store locally
        if url_or_path and 'drive.google.com' in url_or_path and restaurant_name:
            # Try to download the image from Google Drive
            local_path = download_google_drive_image(url_or_path, restaurant_name)
            
            if local_path and os.path.exists(local_path):
                try:
                    img = Image.open(local_path)
                    # Resize for display
                    img.thumbnail((80, 80), Image.LANCZOS)
                    return img
                except Exception as e:
                    print(f"Error loading downloaded Google Drive image: {e}")
            
            # If download failed, use a placeholder
            print(f"Using placeholder for Google Drive image: {url_or_path}")
            # Create a unique filename based on the URL for caching
            url_hash = hashlib.md5(url_or_path.encode()).hexdigest()
            cache_path = os.path.join("cached_images", f"{url_hash}.png")
            
            # Check if we already have this image cached
            if os.path.exists(cache_path):
                try:
                    return Image.open(cache_path)
                except Exception:
                    # If cached image is corrupted, remove it
                    os.remove(cache_path)
            
            # Create a nicer placeholder for Google Drive images
            img = Image.new('RGB', (80, 80), color=(240, 240, 240))
            draw = ImageDraw.Draw(img)
            
            # Draw a light border
            draw.rectangle([(0, 0), (79, 79)], outline=(200, 200, 200))
            
            # Draw a Google Drive-like icon (simplified)
            draw.rectangle([(20, 25), (60, 55)], fill=(66, 133, 244))
            
            # Save to cache
            img.save(cache_path, format="PNG")
            return img
        
        # Check if it's a URL or local path
        elif url_or_path and url_or_path.startswith(('http://', 'https://')):
            # Create a unique filename based on the URL
            url_hash = hashlib.md5(url_or_path.encode()).hexdigest()
            cache_path = os.path.join("cached_images", f"{url_hash}.png")
            
            # Check if we already have this image cached
            if os.path.exists(cache_path):
                try:
                    return Image.open(cache_path)
                except Exception:
                    # If cached image is corrupted, remove it
                    os.remove(cache_path)
            
            # It's a URL, download and cache it
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                response = requests.get(url_or_path, timeout=10, headers=headers)
                
                if response.status_code != 200:
                    print(f"Failed to load image, status code: {response.status_code}")
                    return create_empty_box((80, 80))
                
                img = Image.open(BytesIO(response.content))
                
                # Convert RGBA to RGB if needed to avoid transparency issues
                if img.mode == 'RGBA':
                    # Create a white background
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    # Paste the image on the background
                    background.paste(img, mask=img.split()[3])  # 3 is the alpha channel
                    img = background
                
                # Resize to standard size
                img.thumbnail((80, 80), Image.LANCZOS)
                
                # Save to cache
                img.save(cache_path, format="PNG")
                return img
            except Exception as e:
                print(f"Could not load image from URL {url_or_path}: {e}")
                return create_empty_box((80, 80))
        else:
            # It's a local path
            if os.path.exists(url_or_path):
                return Image.open(url_or_path)
            else:
                return create_empty_box((80, 80))
    except Exception as e:
        print(f"Could not load image: {e}")
        return create_empty_box((80, 80))

def create_placeholder_image():
    """Create a placeholder image with text when image can't be loaded"""
    # Create a blank white image
    width, height = 80, 80
    img = Image.new('RGB', (width, height), color=(240, 240, 240))
    
    # Return the placeholder image
    return img
