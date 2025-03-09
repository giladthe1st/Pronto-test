"""
Logo display functionality for restaurant UI.
"""
import streamlit as st
from utils.image_handler import display_logo

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
            # Use HTML-based display with base64 encoding for better compatibility in deployed environments
            html = display_logo(logo_url, restaurant_name)
            st.markdown(html, unsafe_allow_html=True)
        else:
            # Display a placeholder for restaurants without logos
            st.markdown(
                '<div style="width:140px;height:140px;border:1px solid #ddd;display:flex;align-items:center;justify-content:center;color:#999;">No Logo</div>',
                unsafe_allow_html=True
            )
    except Exception as e:
        # Fallback in case of any errors
        st.markdown(
            '<div style="width:140px;height:140px;border:1px solid #ddd;display:flex;align-items:center;justify-content:center;color:#999;">Error</div>',
            unsafe_allow_html=True
        )
        st.error(f"Error displaying logo: {e}")
