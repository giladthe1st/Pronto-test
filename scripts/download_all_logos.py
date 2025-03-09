"""
Script to download all restaurant logos for deployment.
This script should be run before deployment to ensure all logos are available.
"""
import os
import sys
import time
import shutil
from pathlib import Path

# Add the parent directory to the path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent))

from utils.drive_utils import get_file_id_from_drive_url, download_with_credentials, GOOGLE_DRIVE_API_AVAILABLE
from utils.image_handler import get_cache_path, ensure_cache_directory, create_safe_filename
from database.supabase_client import get_restaurants

# Constants
STATIC_LOGOS_DIR = "static/logos"

def download_all_restaurant_logos():
    """
    Download all restaurant logos from the database and save them to the cache directory.
    Also copies them to the static directory for deployment.
    """
    if not GOOGLE_DRIVE_API_AVAILABLE:
        print("Error: Google Drive API is not available. Cannot download logos.")
        return False
    
    print("Starting download of all restaurant logos...")
    
    # Ensure the cache directory exists
    ensure_cache_directory()
    
    # Ensure the static logos directory exists
    if not os.path.exists(STATIC_LOGOS_DIR):
        os.makedirs(STATIC_LOGOS_DIR)
        print(f"Created static logos directory: {STATIC_LOGOS_DIR}")
    
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
    copied_count = 0
    
    # Download logos for each restaurant
    for restaurant in restaurants:
        restaurant_name = restaurant.get('name', 'Unknown')
        logo_url = restaurant.get('logo_url')
        
        if not logo_url:
            print(f"Skipping {restaurant_name}: No logo URL")
            skipped_count += 1
            continue
        
        # Generate cache path
        cache_path = get_cache_path(logo_url, restaurant_name)
        
        # Generate static path
        url_hash = os.path.basename(cache_path).split('_')[-1]
        safe_name = create_safe_filename(restaurant_name)
        static_path = os.path.join(STATIC_LOGOS_DIR, f"{safe_name}_{url_hash}")
        
        # Check if already in static directory
        if os.path.exists(static_path):
            print(f"Skipping {restaurant_name}: Logo already in static directory at {static_path}")
            skipped_count += 1
            continue
        
        # Check if in cache but not in static
        if os.path.exists(cache_path) and not os.path.exists(static_path):
            try:
                shutil.copy2(cache_path, static_path)
                print(f"Copied logo for {restaurant_name} from cache to static directory: {static_path}")
                copied_count += 1
                continue
            except Exception as e:
                print(f"Error copying logo from cache to static directory for {restaurant_name}: {e}")
                # Continue to download if copy fails
        
        # Skip if already downloaded to cache and copying to static succeeded
        if os.path.exists(cache_path) and os.path.exists(static_path):
            print(f"Skipping {restaurant_name}: Logo already cached at {cache_path} and in static directory")
            skipped_count += 1
            continue
        
        # Extract file ID from Google Drive URL
        file_id = get_file_id_from_drive_url(logo_url)
        if not file_id:
            print(f"Failed to extract file ID from URL for {restaurant_name}: {logo_url}")
            failure_count += 1
            continue
        
        print(f"Downloading logo for {restaurant_name}...")
        
        # Download the logo
        try:
            result = download_with_credentials(file_id, cache_path)
            if result:
                print(f"Successfully downloaded logo for {restaurant_name} to {cache_path}")
                success_count += 1
                
                # Copy to static directory
                try:
                    shutil.copy2(cache_path, static_path)
                    print(f"Copied logo for {restaurant_name} to static directory: {static_path}")
                    copied_count += 1
                except Exception as e:
                    print(f"Error copying logo to static directory for {restaurant_name}: {e}")
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
    print(f"Copied to static directory: {copied_count}")
    print(f"Failed to download: {failure_count}")
    print(f"Skipped (already cached or no URL): {skipped_count}")
    
    return success_count > 0 or copied_count > 0

if __name__ == "__main__":
    if download_all_restaurant_logos():
        print("\nAll available logos have been downloaded and copied to the static directory.")
        print("You can now deploy the application with the pre-downloaded logos.")
    else:
        print("\nFailed to download or copy logos. Please check the errors above.")
