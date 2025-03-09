"""
UI components for displaying restaurant information in the Pronto application.
"""
import streamlit as st

# Import components from individual modules
from ui.components.styling import apply_restaurant_styling
from ui.components.logo_display import display_restaurant_logo
from ui.components.deal_display import display_deal_section
from ui.components.menu_display import display_menu_section
from ui.components.reviews_display import display_reviews_section
from ui.components.location_display import display_location_section

def display_restaurants(restaurants, flyer_existence=None, user_location=None, text_filter=""):
    """
    Display a list of restaurants with their details.
    
    Args:
        restaurants: List of restaurant dictionaries
        flyer_existence: Dictionary of pre-checked flyer existence by restaurant name
        user_location: Dictionary containing user's latitude and longitude
        text_filter: Text to filter deals by
    """
    if not restaurants:
        st.info("No restaurants found. Please check your data source or adjust your filters.")
        return
    
    # Apply styling
    apply_restaurant_styling()
    
    # Display each restaurant
    for i, restaurant in enumerate(restaurants):
        display_single_restaurant(restaurant, user_location, text_filter)
        
        # Add a divider after each restaurant except the last one
        if i < len(restaurants) - 1:
            st.markdown('<div class="restaurant-divider"></div>', unsafe_allow_html=True)

def display_single_restaurant(restaurant, user_location=None, text_filter=""):
    """
    Display a single restaurant with all its components.
    
    Args:
        restaurant: Dictionary containing restaurant information
        user_location: Dictionary containing user's latitude and longitude
        text_filter: Text to filter deals by
    """
    # Create a row for each restaurant
    with st.container():
        # Use 6 columns for better organization
        col1, col2, col3, col4, col5, col6 = st.columns([1, 1.5, 1, 1, 1.5, 1.5])
        
        # Column 1: Logo
        with col1:
            display_restaurant_logo(restaurant['name'], restaurant.get('logo_url'))
        
        # Column 2: Name
        with col2:
            # Add the same fixed vertical space before name
            st.markdown('<div class="vertical-spacer"></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="restaurant-name"><a href="{restaurant["website"]}" target="_blank">{restaurant["name"]}</a></div>', unsafe_allow_html=True)
            
        
        # Column 3: Deals
        with col3:
            display_deal_section(restaurant, text_filter)
        
        # Column 4: Menu
        with col4:
            display_menu_section(restaurant)
        
        # Column 5: Reviews
        with col5:
            display_reviews_section(restaurant)
        
        # Column 6: Location, Distance, Maps
        with col6:
            display_location_section(restaurant, user_location)
