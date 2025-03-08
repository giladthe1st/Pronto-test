"""
Logo display functionality for restaurant UI.
"""
import os
import streamlit as st
from PIL import Image
from utils.image_utils import download_google_drive_image

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
    
    # Create a safe filename from the restaurant name
    safe_name = restaurant_name.lower().replace(' ', '_').replace('&', '_').replace("'", "")
    logo_path = f"logo_images/{safe_name}_logo.png"
    
    if os.path.exists(logo_path):
        # Load and resize the logo image
        img = Image.open(logo_path)
        # Maintain aspect ratio but ensure consistent size
        img.thumbnail((140, 140), Image.LANCZOS)
        st.image(img, use_column_width=False, width=140)
    else:
        # Attempt to download logo if we have a URL
        if logo_url:
            downloaded_path = download_google_drive_image(logo_url, restaurant_name)
            if downloaded_path:
                img = Image.open(downloaded_path)
                # Maintain aspect ratio but ensure consistent size
                img.thumbnail((140, 140), Image.LANCZOS)
                st.image(img, use_column_width=False, width=140)
            else:
                st.markdown('<span style="font-size: 80px; color: #666;">🍽️</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span style="font-size: 80px; color: #666;">🍽️</span>', unsafe_allow_html=True)
