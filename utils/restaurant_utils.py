"""
Utility functions for restaurant data processing in the Pronto application.
"""
import streamlit as st

# Import functionality from modular utility files
from utils.review_utils import parse_reviews
from utils.location_utils import extract_coordinates_from_maps_url, get_winnipeg_coordinates_by_area, get_user_location_from_ip, geocode_address
from utils.data_utils import download_google_sheet_data
from utils.distance_utils import calculate_distance

# Re-export functions to maintain backward compatibility
__all__ = ['process_restaurant_data', 'download_google_sheet_data', 'get_user_location_from_ip', 'calculate_distance']

@st.cache_data(ttl=3600)  # Cache for 1 hour
def process_restaurant_data(df):
    """
    Process the restaurant data from a pandas DataFrame.
    
    Args:
        df: Pandas DataFrame containing restaurant data
        
    Returns:
        List of restaurant dictionaries with processed data
    """
    if df is not None and not df.empty:
        # Convert DataFrame to list of dictionaries
        restaurants = df.to_dict('records')
        
        # Process each restaurant
        for restaurant in restaurants:
            restaurant_name = restaurant.get('name', 'Unknown Restaurant')
            
            # Check if 'reviews_data' key exists before trying to access it (new format)
            if 'reviews_data' in restaurant and restaurant['reviews_data']:
                print(f"Processing reviews for {restaurant_name} using reviews_data: {restaurant['reviews_data']}")
                rating, count = parse_reviews(restaurant['reviews_data'])
                print(f"Parsed rating: {rating}, count: {count}")
            # Fall back to 'reviews' key if 'reviews_data' doesn't exist (backward compatibility)
            elif 'reviews' in restaurant and restaurant['reviews']:
                print(f"Processing reviews for {restaurant_name} using reviews: {restaurant['reviews']}")
                rating, count = parse_reviews(restaurant['reviews'])
                print(f"Parsed rating: {rating}, count: {count}")
            else:
                # Default values if both review keys are missing
                rating, count = 0.0, 0
                print(f"No reviews for {restaurant_name}, using defaults")
                
            restaurant['rating'] = rating
            restaurant['review_count'] = count
            
            # Add default distance if missing
            if 'distance' not in restaurant:
                restaurant['distance'] = 'Unknown'  # Default distance value
            
            # Get coordinates using the restaurant's address
            has_coordinates = False
            
            # First, try to get coordinates from the address field
            if 'address' in restaurant and restaurant['address']:
                print(f"Geocoding address for {restaurant_name}: {restaurant['address']}")
                lat, lng = geocode_address(restaurant['address'])
                if lat is not None and lng is not None:
                    restaurant['latitude'] = lat
                    restaurant['longitude'] = lng
                    has_coordinates = True
                    print(f"Successfully geocoded address for {restaurant_name}")
            
            # If we couldn't get coordinates from the address, try the maps_url as a fallback
            if not has_coordinates and 'maps_url' in restaurant and restaurant['maps_url']:
                print(f"Falling back to maps_url for {restaurant_name}")
                lat, lng = extract_coordinates_from_maps_url(restaurant['maps_url'])
                if lat is not None and lng is not None:
                    restaurant['latitude'] = lat
                    restaurant['longitude'] = lng
                    has_coordinates = True
            
            # If we still don't have coordinates, try to get them from the location
            if not has_coordinates and 'location' in restaurant:
                print(f"Using location area for {restaurant_name}: {restaurant['location']}")
                # Use known locations in Winnipeg
                lat, lng = get_winnipeg_coordinates_by_area(restaurant['location'])
                restaurant['latitude'] = lat
                restaurant['longitude'] = lng
                has_coordinates = True
            
            # Final check - if we still don't have coordinates, use downtown Winnipeg
            if not has_coordinates:
                print(f"No coordinates found for {restaurant_name}, using downtown Winnipeg")
                restaurant['latitude'] = 49.8951
                restaurant['longitude'] = -97.1384
            
        return restaurants
    else:
        return []
