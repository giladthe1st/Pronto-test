"""
Script to download an image from Google Drive using the Google Drive API with credentials.
This script uses the download_with_credentials function from drive_utils.py.
"""
import os
import sys
import argparse

# Add the parent directory to the path so we can import from utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.drive_utils import get_file_id_from_drive_url, download_with_credentials, DEFAULT_LOGO_SIZE

def main():
    parser = argparse.ArgumentParser(description="Download a file from Google Drive using credentials")
    parser.add_argument("--url", type=str, 
                        default="https://drive.google.com/file/d/19xqBh-6QOZgXxdq-o2T-i5cFsqvU4PyX/view?usp=sharing",
                        help="Google Drive URL of the file")
    parser.add_argument("--output", type=str, 
                        default=None,
                        help="Output path for the downloaded file")
    parser.add_argument("--size", type=int, nargs=2,
                        default=DEFAULT_LOGO_SIZE,
                        help="Size of the output image (width height)")
    
    args = parser.parse_args()
    
    # Extract file ID from URL
    file_id = get_file_id_from_drive_url(args.url)
    if not file_id:
        print(f"Could not extract file ID from URL: {args.url}")
        sys.exit(1)
        
    print(f"Extracted file ID: {file_id}")
    
    # Determine output path
    if args.output:
        output_path = args.output
    else:
        # Generate a default output path based on the file ID
        output_dir = "downloaded_images"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{file_id}.png")
    
    # Download the file
    img = download_with_credentials(file_id, output_path, tuple(args.size))
    
    if img:
        print(f"Successfully downloaded image to: {output_path}")
        print(f"Image size: {img.size}")
    else:
        print("Failed to download image")
        sys.exit(1)

if __name__ == "__main__":
    main()
