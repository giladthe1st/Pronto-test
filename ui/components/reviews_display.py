"""
Reviews display functionality for restaurant UI.
"""
import streamlit as st

def display_reviews_section(restaurant):
    """
    Display the reviews section for a restaurant.
    
    Args:
        restaurant: Dictionary containing restaurant information
    """
    st.markdown("<div class='section-header'>Reviews</div>", unsafe_allow_html=True)
    
    # Check if we have the new reviews_data format
    if 'reviews_data' in restaurant and restaurant['reviews_data']:
        # Display reviews_data content directly with line breaks
        reviews_data = restaurant['reviews_data'].replace('\n', '<br>')
        st.markdown(f"<div class='restaurant-reviews'>{reviews_data}</div>", unsafe_allow_html=True)
    
    # Fall back to old format if reviews_data is not available
    elif 'reviews' in restaurant and restaurant['reviews']:
        st.markdown(f"<div class='restaurant-reviews'>{restaurant['reviews']}</div>", unsafe_allow_html=True)
    
    else:
        st.info("No reviews available for this restaurant.")