"""
Location display functionality for restaurant UI.
"""
import streamlit as st
from utils.restaurant_utils import calculate_distance

def display_location_section(restaurant, user_location=None):
    """
    Display the location section for a restaurant.
    
    Args:
        restaurant: Dictionary containing restaurant information
        user_location: Dictionary containing user's latitude and longitude
    """
    st.markdown("<div class='section-header'>Location</div>", unsafe_allow_html=True)
    
    # Safely get location with fallback
    location = restaurant.get('location', 'Address not available')
    st.markdown(f"<div class='restaurant-location'><strong>Address:</strong> {location}</div>", unsafe_allow_html=True)
    
    # Calculate and display distance if we have both user location and restaurant coordinates
    has_user_location = user_location and user_location['latitude'] is not None and user_location['longitude'] is not None
    has_restaurant_coords = 'latitude' in restaurant and 'longitude' in restaurant and restaurant['latitude'] is not None and restaurant['longitude'] is not None
    
    if has_user_location and has_restaurant_coords:
        display_calculated_distance(restaurant, user_location)
    else:
        # Display default distance if we don't have coordinates
        st.markdown(f"<div class='restaurant-distance'><strong>Distance:</strong> {restaurant.get('distance', 'Unknown')}</div>", unsafe_allow_html=True)
    
    # Display Google Maps link if available
    maps_url = restaurant.get('maps_url', '')
    if maps_url:
        st.markdown(f"<div class='restaurant-info'><a href='{maps_url}' target='_blank'>📍 Get Directions</a></div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='restaurant-info'>📍 Directions not available</div>", unsafe_allow_html=True)

def display_calculated_distance(restaurant, user_location):
    """
    Calculate and display the distance between user and restaurant.
    
    Args:
        restaurant: Dictionary containing restaurant information
        user_location: Dictionary containing user's latitude and longitude
    """
    # Calculate distance using the Haversine formula
    distance_km = calculate_distance(
        user_location['latitude'], 
        user_location['longitude'],
        restaurant['latitude'], 
        restaurant['longitude']
    )
    
    # Convert to miles
    distance_mi = distance_km * 0.621371
    
    # Format distance for display
    if distance_mi < 0.1:
        distance_text = "less than 0.1 mi"
        # Store the actual value for filtering
        restaurant['distance'] = "0.1 mi"
    else:
        distance_text = f"{distance_mi:.1f} mi"
        # Store the actual value for filtering
        restaurant['distance'] = f"{distance_mi:.1f} mi"
    
    st.markdown(f"<div class='restaurant-distance'><strong>Distance:</strong> {distance_text}</div>", unsafe_allow_html=True)
