"""
Utility functions for loading and processing restaurant data from the database.
"""
import streamlit as st
from database.supabase_client import get_restaurants, process_restaurant_data_from_db
from utils.location_utils import get_user_location_from_ip
from utils.distance_utils import calculate_distance

@st.cache_data(ttl=3600, show_spinner=False)  # Cache for 1 hour, hide default spinner
def load_restaurant_data_from_db(filters=None):
    """
    Load restaurant data from the database with optional filtering.
    
    Args:
        filters (dict, optional): Dictionary of filter conditions
        
    Returns:
        List of processed restaurant dictionaries
    """
    # Create a placeholder for status messages
    status_message = st.empty()
    
    try:
        # Get restaurants from database
        restaurants = get_restaurants(filters=filters)
        
        if restaurants:
            # Process the data to ensure it has all required fields
            processed_restaurants = process_restaurant_data_from_db(restaurants)
            return processed_restaurants
        else:
            status_message.warning("No restaurant data found in the database.")
            return []
    except Exception as e:
        error_msg = f"Error loading restaurant data from database: {e}"
        status_message.error(error_msg)
        print(f"ERROR: {error_msg}")
        return []

def process_restaurant_locations(restaurants):
    """
    Process location data for restaurants, calculating distances from user location.
    
    Args:
        restaurants: List of restaurant dictionaries
        
    Returns:
        List of restaurant dictionaries with distance information
    """
    if not restaurants:
        return []
    
    # Get user location from session state or IP
    if 'user_location' not in st.session_state:
        st.session_state.user_location = get_user_location_from_ip()
    
    user_location = st.session_state.user_location
    
    # Calculate distance for each restaurant
    for restaurant in restaurants:
        has_user_location = user_location and user_location['latitude'] is not None and user_location['longitude'] is not None
        has_restaurant_coords = 'latitude' in restaurant and 'longitude' in restaurant and restaurant['latitude'] is not None and restaurant['longitude'] is not None
        
        if has_user_location and has_restaurant_coords:
            # Calculate distance using the Haversine formula
            distance_km = calculate_distance(
                user_location['latitude'], 
                user_location['longitude'],
                restaurant['latitude'], 
                restaurant['longitude']
            )
            
            # Convert to miles
            distance_mi = distance_km * 0.621371
            
            # Store the formatted distance for filtering
            if distance_mi < 0.1:
                restaurant['distance'] = "0.1 mi"
            else:
                restaurant['distance'] = f"{distance_mi:.1f} mi"
    
    return restaurants
