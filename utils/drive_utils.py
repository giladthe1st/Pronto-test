"""
Utility functions for interacting with Google Drive in the Pronto application.
"""
import os
import io
from PIL import Image
import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env file (for local development)
load_dotenv()

# Constants
DEFAULT_LOGO_SIZE = (140, 140)
CREDENTIALS_PATH = "credentials.json"

# Flag to track if Google Drive API is available
GOOGLE_DRIVE_API_AVAILABLE = False

# Try to import Google Drive API libraries, but don't fail if they're not available
try:
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseDownload
    from google.oauth2 import service_account
    GOOGLE_DRIVE_API_AVAILABLE = True
except ImportError:
    print("Google Drive API libraries not available. Some functionality will be limited.")

def get_drive_credentials():
    """
    Get Google Drive API credentials from either Streamlit secrets or local file.
    Streamlit secrets take precedence for deployed environments.
    
    Returns:
        google.oauth2.service_account.Credentials: Service account credentials or None if not available
    """
    if not GOOGLE_DRIVE_API_AVAILABLE:
        print("Google Drive API libraries not available. Cannot get credentials.")
        return None
        
    try:
        # First try to get from Streamlit secrets (for deployed app)
        if 'google_drive' in st.secrets:
            # Create credentials from the secrets dictionary
            service_account_info = st.secrets["google_drive"]
            credentials = service_account.Credentials.from_service_account_info(
                service_account_info,
                scopes=['https://www.googleapis.com/auth/drive.readonly']
            )
            print("Using Google Drive credentials from Streamlit secrets")
            return credentials
        
        # Then try to get from local credentials file (for local development)
        if os.path.exists(CREDENTIALS_PATH):
            credentials = service_account.Credentials.from_service_account_file(
                CREDENTIALS_PATH,
                scopes=['https://www.googleapis.com/auth/drive.readonly']
            )
            print(f"Using Google Drive credentials from local file: {CREDENTIALS_PATH}")
            return credentials
        
        print("No Google Drive credentials found")
        return None
    except Exception as e:
        print(f"Error getting Google Drive credentials: {e}")
        return None

def get_file_id_from_drive_url(url):
    """
    Extract the file ID from various Google Drive URL formats.
    
    Args:
        url (str): Google Drive URL
        
    Returns:
        str: File ID or None if not found
    """
    if not url or not isinstance(url, str):
        return None
    
    try:    
        # Pattern 1: https://drive.google.com/file/d/{file_id}/view
        if '/file/d/' in url:
            return url.split('/file/d/')[1].split('/')[0]
        # Pattern 2: https://drive.google.com/open?id={file_id}
        elif 'open?id=' in url:
            return url.split('open?id=')[1].split('&')[0]
        # Pattern 3: https://drive.google.com/uc?id={file_id}
        elif 'uc?id=' in url:
            return url.split('uc?id=')[1].split('&')[0]
        # Pattern 4: https://drive.google.com/drive/folders/{file_id}
        elif '/drive/folders/' in url:
            return url.split('/drive/folders/')[1].split('?')[0].split('/')[0]
    except Exception as e:
        print(f"Error extracting file ID from URL '{url}': {e}")
    
    return None

def download_with_credentials(file_id, cache_path, size=DEFAULT_LOGO_SIZE):
    """
    Download a file from Google Drive using the Google Drive API with credentials.
    
    Args:
        file_id (str): The ID of the file to download
        cache_path (str): Path where the file should be saved
        size (tuple): Target size for the image
        
    Returns:
        PIL.Image or None: Processed image or None if failed
    """
    # Check if Google Drive API is available
    if not GOOGLE_DRIVE_API_AVAILABLE:
        print("Google Drive API libraries not available. Cannot download file.")
        return None
        
    try:
        print(f"Using credentials to download file with ID: {file_id}")
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        
        # Get credentials
        credentials = get_drive_credentials()
        if not credentials:
            print("Failed to get Google Drive credentials")
            return None
        
        # Build the Drive API client
        drive_service = build('drive', 'v3', credentials=credentials)
        
        # Get file metadata to check if it exists and get its MIME type
        try:
            file_metadata = drive_service.files().get(fileId=file_id).execute()
            print(f"File metadata: {file_metadata}")
        except Exception as e:
            print(f"Error getting file metadata: {e}")
            return None
        
        # Download the file
        request = drive_service.files().get_media(fileId=file_id)
        file_buffer = io.BytesIO()
        downloader = MediaIoBaseDownload(file_buffer, request)
        
        done = False
        while not done:
            status, done = downloader.next_chunk()
            print(f"Download progress: {int(status.progress() * 100)}%")
        
        # Process the image
        file_buffer.seek(0)
        try:
            img = Image.open(file_buffer)
            
            # Convert RGBA to RGB if needed
            if img.mode == 'RGBA':
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])
                img = background
            
            # Resize while maintaining aspect ratio
            img.thumbnail(size, Image.LANCZOS)
            
            # Save to cache
            img.save(cache_path, format="PNG")
            print(f"Successfully saved image to: {cache_path}")
            return img
        except Exception as e:
            print(f"Error processing image: {e}")
            return None
            
    except Exception as e:
        print(f"Error downloading file: {e}")
        return None
