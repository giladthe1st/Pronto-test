"""
Script to download all restaurant logos for deployment.
This script should be run before deployment to ensure all logos are available in the static directory.
"""
import os
import sys
import time
from pathlib import Path

# Add the parent directory to the path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent))

from utils.drive_utils import get_file_id_from_drive_url, download_with_credentials, GOOGLE_DRIVE_API_AVAILABLE
from utils.image_handler import get_static_path, ensure_static_directory
from database.supabase_client import get_restaurants

def download_all_restaurant_logos():
    """
    Download all restaurant logos from the database and save them to the static directory.
    """
    if not GOOGLE_DRIVE_API_AVAILABLE:
        print("Error: Google Drive API is not available. Cannot download logos.")
        return False
    
    print("Starting download of all restaurant logos...")
    
    # Ensure the static logos directory exists
    ensure_static_directory()
    
    # Get all restaurants from the database
    restaurants = get_restaurants()
    if not restaurants:
        print("No restaurants found in the database.")
        return False
    
    print(f"Found {len(restaurants)} restaurants.")
    
    # Track success and failures
    success_count = 0
    failure_count = 0
    skipped_count = 0
    
    # Download logos for each restaurant
    for restaurant in restaurants:
        restaurant_name = restaurant.get('name', 'Unknown')
        logo_url = restaurant.get('logo_url')
        
        if not logo_url:
            print(f"Skipping {restaurant_name}: No logo URL")
            skipped_count += 1
            continue
        
        # Generate static path
        static_path = get_static_path(logo_url, restaurant_name)
        
        # Skip if already in static directory
        if os.path.exists(static_path):
            print(f"Skipping {restaurant_name}: Logo already in static directory at {static_path}")
            skipped_count += 1
            continue
        
        # Extract file ID from Google Drive URL
        file_id = get_file_id_from_drive_url(logo_url)
        if not file_id:
            print(f"Failed to extract file ID from URL for {restaurant_name}: {logo_url}")
            failure_count += 1
            continue
        
        print(f"Downloading logo for {restaurant_name}...")
        
        # Download the logo directly to the static directory
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(static_path), exist_ok=True)
            
            # Download the logo
            result = download_with_credentials(file_id, static_path)
            if result:
                print(f"Successfully downloaded logo for {restaurant_name} to {static_path}")
                success_count += 1
            else:
                print(f"Failed to download logo for {restaurant_name}")
                failure_count += 1
            
            # Add a small delay to avoid rate limiting
            time.sleep(0.5)
        except Exception as e:
            print(f"Error downloading logo for {restaurant_name}: {e}")
            failure_count += 1
    
    # Print summary
    print("\nDownload Summary:")
    print(f"Total restaurants: {len(restaurants)}")
    print(f"Successfully downloaded: {success_count}")
    print(f"Failed to download: {failure_count}")
    print(f"Skipped (already in static directory or no URL): {skipped_count}")
    
    return success_count > 0

if __name__ == "__main__":
    if download_all_restaurant_logos():
        print("\nAll available logos have been downloaded to the static directory.")
        print("You can now deploy the application with the pre-downloaded logos.")
    else:
        print("\nFailed to download logos. Please check the errors above.")
