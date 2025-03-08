"""
Script to download an image from Google Drive.
This script uses requests and Google authentication to download a specific file.
"""
import os
import requests
from google_auth import get_google_credentials

def download_file_from_drive(file_id, output_path, credentials_path=None):
    """
    Download a file from Google Drive using its file ID.
    
    Args:
        file_id (str): The ID of the file to download.
        output_path (str): The path where the downloaded file will be saved.
        credentials_path (str, optional): Path to the service account JSON file.
            If None, will try to use environment variables.
    
    Returns:
        bool: True if download was successful, False otherwise.
    """
    try:
        # Get credentials
        credentials = get_google_credentials(credentials_path)
        if not credentials:
            print("Failed to get Google credentials.")
            return False
        
        # Create a session with the credentials
        session = requests.Session()
        access_token = credentials.get_access_token().access_token
        session.headers.update({"Authorization": f"Bearer {access_token}"})
        
        # Direct download URL format
        download_url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media"
        
        # Download the file with progress tracking
        response = session.get(download_url, stream=True)
        
        # Check if the request was successful
        if response.status_code != 200:
            print(f"Failed to download file. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        # Get total file size if available
        total_size = int(response.headers.get('content-length', 0))
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save the file to the specified path
        downloaded_size = 0
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    if total_size > 0:
                        progress = int(downloaded_size / total_size * 100)
                        print(f"Download progress: {progress}%", end="\r")
        
        print(f"\nFile successfully downloaded to {output_path}")
        return True
    
    except Exception as e:
        print(f"Error downloading file: {e}")
        return False

if __name__ == "__main__":
    # Extract file ID from the Google Drive URL
    # URL format: https://drive.google.com/file/d/FILE_ID/view?usp=drive_link
    file_url = "https://drive.google.com/file/d/1NFLS0KG6J4F_Jd80RFWb6gAInYNt7vL3/view?usp=drive_link"
    file_id = file_url.split('/d/')[1].split('/')[0]
    
    # Set the output path
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "downloaded_image.jpg")
    
    # Download the file using the credentials.json file
    credentials_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "credentials.json")
    download_file_from_drive(file_id, output_path, credentials_path)
