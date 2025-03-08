"""
Filter components for the Pronto application.
"""
import streamlit as st

def get_distance_value(restaurant):
    """
    Safely extract distance value from a restaurant dictionary.
    
    Args:
        restaurant: Restaurant dictionary
        
    Returns:
        float: Distance value in miles, defaults to 0.0 if not available
    """
    try:
        if 'distance' in restaurant:
            parts = restaurant['distance'].split()
            if parts and len(parts) > 0:
                return float(parts[0])
        return 0.0
    except (ValueError, IndexError, TypeError):
        return 0.0

def display_filters(restaurants):
    """
    Display filter controls for restaurants.
    
    Args:
        restaurants: List of restaurant dictionaries
        
    Returns:
        tuple: (filtered_restaurants, distance_filter, min_rating, min_reviews, sort_by, sort_order, text_filter)
    """
    if not restaurants:
        return [], 0, 0, 0, "Distance", "Descending", ""
    
    # Add text filter at the top
    text_filter = st.text_input("Search deals by text", placeholder="Type to filter deals...")
    
    # Create 5 columns for filters in one line
    filter_col1, filter_col2, filter_col3, filter_col4, filter_col5 = st.columns(5)
    
    # Distance filter
    with filter_col1:
        # Safely get max distance with error handling
        distances = [get_distance_value(r) for r in restaurants]
        max_distance = max(distances) if distances else 10.0  # Default to 10 miles if no data
        
        # Ensure max_distance is greater than 0 to prevent RangeError
        if max_distance <= 0.0:
            max_distance = 10.0  # Default to 10 miles if all distances are 0
        
        distance_filter = st.slider(
            "Max Distance (mi)",
            0.0, max_distance, max_distance, 0.1
        )
    
    # Rating filter
    with filter_col2:
        min_rating = st.slider(
            "Min Rating",
            0.0, 10.0, 0.0, 0.5
        )
    
    # Review count filter
    with filter_col3:
        max_reviews = max([r.get('review_count', 0) for r in restaurants]) if restaurants else 100
        # Ensure max is at least 1 more than min to prevent RangeError
        if max_reviews == 0:
            max_reviews = 1
        
        min_reviews = st.slider(
            "Min Reviews",
            0, max_reviews, 0
        )
    
    # Sort by option
    with filter_col4:
        sort_by = st.selectbox(
            "Sort By",
            ["Distance", "Rating", "Review Count"]
        )
    
    # Sort order option
    with filter_col5:
        sort_order = st.radio(
            "Sort Order",
            ["Ascending", "Descending"],
            horizontal=True
        )
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Apply filters and sorting
    filtered_restaurants = apply_filters_and_sorting(
        restaurants, distance_filter, min_rating, min_reviews, sort_by, sort_order, text_filter
    )
    
    # Show how many restaurants match the filters
    st.subheader(f"Found {len(filtered_restaurants)} restaurants")
    
    return filtered_restaurants, distance_filter, min_rating, min_reviews, sort_by, sort_order, text_filter

def apply_filters_and_sorting(restaurants, distance_filter, min_rating, min_reviews, sort_by, sort_order, text_filter=""):
    """
    Apply filters and sorting to the restaurant list.
    
    Args:
        restaurants: List of restaurant dictionaries
        distance_filter: Maximum distance in miles
        min_rating: Minimum rating (0-10)
        min_reviews: Minimum number of reviews
        sort_by: Field to sort by ("Distance", "Rating", or "Review Count")
        sort_order: Sort order ("Ascending" or "Descending")
        text_filter: Text to filter deals by
        
    Returns:
        list: Filtered and sorted list of restaurants
    """
    if not restaurants:
        return []
    
    # Apply distance filter using the helper function
    filtered = [r for r in restaurants if get_distance_value(r) <= distance_filter]
    
    # Normalize min_rating from 0-10 scale to 0-5 scale used internally
    normalized_min_rating = (min_rating / 10) * 5
    
    # Apply review filters with safe access
    filtered = [r for r in filtered if r.get('rating', 0) >= normalized_min_rating and r.get('review_count', 0) >= min_reviews]
    
    # Apply text filter if provided
    if text_filter:
        text_filter = text_filter.lower()
        filtered_by_text = []
        
        for restaurant in filtered:
            # Check for matches in different deal structures
            deal_match = False
            
            # Check new deal structure (summarized_deals and detailed_deals)
            if 'summarized_deals' in restaurant and restaurant['summarized_deals']:
                if text_filter in restaurant['summarized_deals'].lower():
                    deal_match = True
            
            if not deal_match and 'detailed_deals' in restaurant and restaurant['detailed_deals']:
                if text_filter in restaurant['detailed_deals'].lower():
                    deal_match = True
            
            # Check legacy deal structure
            if not deal_match and 'deals' in restaurant and restaurant['deals']:
                if text_filter in restaurant['deals'].lower():
                    deal_match = True
            
            # Also check restaurant name for matches
            if not deal_match and 'name' in restaurant and restaurant['name']:
                if text_filter in restaurant['name'].lower():
                    deal_match = True
                    
            # Include restaurant if any match found
            if deal_match:
                filtered_by_text.append(restaurant)
        
        filtered = filtered_by_text
    
    # Apply sorting with safe access
    if sort_by == "Distance":
        filtered.sort(key=lambda r: get_distance_value(r), reverse=(sort_order == "Descending"))
    elif sort_by == "Rating":
        filtered.sort(key=lambda r: r.get('rating', 0), reverse=(sort_order == "Descending"))
    elif sort_by == "Review Count":
        filtered.sort(key=lambda r: r.get('review_count', 0), reverse=(sort_order == "Descending"))
    
    return filtered
