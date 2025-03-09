"""
Reviews display functionality for restaurant UI.
"""
import streamlit as st
import math

def display_reviews_section(restaurant):
    """
    Display the reviews section for a restaurant.
    
    Args:
        restaurant: Dictionary containing restaurant information
    """
    st.markdown("<div class='section-header'>Reviews</div>", unsafe_allow_html=True)
    
    # Display rating stars if available
    if 'rating' in restaurant and restaurant['rating'] is not None:
        # Convert rating to 5-star scale if needed (some systems use 0-10)
        rating = float(restaurant['rating'])
        if rating > 5:  # If rating is on a 0-10 scale, convert to 0-5
            rating = rating / 2
            
        # Calculate full and half stars
        full_stars = math.floor(rating)
        half_star = 1 if rating - full_stars >= 0.5 else 0
        empty_stars = 5 - full_stars - half_star
        
        # Create star rating HTML
        stars_html = '★' * full_stars
        if half_star:
            stars_html += '½'
        stars_html += '☆' * empty_stars
        
        # Display rating with stars and numeric value
        review_count = restaurant.get('review_count', 0)
        st.markdown(
            f"<div class='rating-stars'>{stars_html} {rating:.1f}/5 ({review_count} reviews)</div>",
            unsafe_allow_html=True
        )
    
    # Check if we have the new reviews_data format
    reviews_data = restaurant.get('reviews_data', '')
    reviews_legacy = restaurant.get('reviews', '')
    
    if reviews_data:
        # Display reviews_data content directly with line breaks
        reviews_data_formatted = reviews_data.replace('\n', '<br>')
        st.markdown(f"<div class='restaurant-reviews'>{reviews_data_formatted}</div>", unsafe_allow_html=True)
    
    # Fall back to old format if reviews_data is not available
    elif reviews_legacy:
        st.markdown(f"<div class='restaurant-reviews'>{reviews_legacy}</div>", unsafe_allow_html=True)
    
    else:
        st.info("No reviews available for this restaurant.")