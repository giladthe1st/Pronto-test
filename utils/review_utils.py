"""
Utility functions for parsing and processing restaurant reviews.
"""
import re
import streamlit as st

@st.cache_data(ttl=3600)  # Cache for 1 hour
def parse_reviews(review_str):
    """
    Parse the reviews string to extract rating and count
    Example format: 
    - Old format: "4.5/5 (120 reviews)" 
    - New format: "Total Reviews: 120\nAverage Rating: 8.6/10"
    
    Returns: (rating, count) where rating is normalized to a 0-5 scale
    """
    try:
        if not review_str:
            return 0.0, 0
            
        # Check if we're using the new format (contains "Total Reviews:" and "Average Rating:")
        if "Total Reviews:" in review_str and "Average Rating:" in review_str:
            # Extract review count - handle both formats: "Total Reviews: 120" and "Total reviews: 120"
            count_match = re.search(r'Total [Rr]eviews:?\s*([0-9,]+)', review_str)
            if count_match:
                # Remove commas from numbers like "2,804"
                count_str = count_match.group(1).replace(',', '')
                count = int(count_str)
            else:
                count = 0
            
            # Extract rating
            rating_match = re.search(r'Average Rating:?\s*(\d+\.\d+|\d+)\/(\d+)', review_str)
            if rating_match:
                rating_value = float(rating_match.group(1))
                max_rating = float(rating_match.group(2))
                
                # Normalize to 5-star scale if needed
                if max_rating != 5:
                    rating = (rating_value / max_rating) * 5
                else:
                    rating = rating_value
            else:
                rating = 0.0
                
            return rating, count
        else:
            # Use the old format parsing logic
            # Extract rating (e.g., 4.5 from "4.5/5" or 8.6 from "8.6/10")
            rating_match = re.search(r'(\d+\.\d+|\d+)\/(\d+)', review_str)
            
            if rating_match:
                rating_value = float(rating_match.group(1))
                max_rating = float(rating_match.group(2))
                
                # Normalize to 5-star scale if needed
                if max_rating != 5:
                    rating = (rating_value / max_rating) * 5
                else:
                    rating = rating_value
            else:
                rating = 0.0
            
            # Extract count (e.g., 120 from "(120 reviews)")
            count_match = re.search(r'\((\d+)\s+reviews\)', review_str)
            count = int(count_match.group(1)) if count_match else 0
            
            return rating, count
    except Exception as e:
        print(f"Error parsing reviews: {e} for review string: '{review_str}'")
        return 0.0, 0
