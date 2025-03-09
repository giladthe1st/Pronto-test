"""
Logo display functionality for restaurant UI.
"""
import streamlit as st
from utils.image_handler import get_logo_from_drive

def display_restaurant_logo(restaurant_name, logo_url=None):
    """
    Display a restaurant logo or placeholder.
    
    Args:
        restaurant_name: Name of the restaurant
        logo_url: Optional URL to download logo from if not found locally
        
    Returns:
        None
    """
    # Add fixed vertical space before logo
    st.markdown('<div class="vertical-spacer"></div>', unsafe_allow_html=True)
    
    try:
        # Get the restaurant logo using our improved image handler
        if logo_url and logo_url.strip():
            # Option 1: Use the streamlit image display
            img = get_logo_from_drive(logo_url, restaurant_name)
            st.image(img, width=140)
            
            # Option 2: Alternative HTML-based display with more control
            # html = display_logo(logo_url, restaurant_name)
            # st.markdown(html, unsafe_allow_html=True)
        else:
            # No logo URL provided, show placeholder
            st.markdown('<span style="font-size: 80px; color: #666;">🍽️</span>', unsafe_allow_html=True)
    except Exception as e:
        # Handle any unexpected errors
        st.error(f"Error displaying logo: {e}")
        # Show a fallback placeholder
        st.markdown('<span style="font-size: 80px; color: #666;">🍽️</span>', unsafe_allow_html=True)
