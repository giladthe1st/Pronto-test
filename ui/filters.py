"""
Filter components for the Pronto application.
"""
import streamlit as st
import re

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

def extract_all_prices_from_deals(restaurant):
    """
    Extract all prices from deals text that have a dollar sign in the format "$Number".
    
    Args:
        restaurant: Restaurant dictionary
        
    Returns:
        list: List of all prices found in deals with dollar signs
    """
    # Only match prices with dollar signs in the format "$Number"
    # Exclude prices that are followed by "each" which typically indicates per-item pricing
    price_pattern = r'\$(\d+(?:\.\d+)?)(?!\s*each)'  # $20 or $20.99, but not "$0.95 each"
    
    prices = []
    
    # Check all possible deal fields
    deal_fields = ['summarized_deals', 'detailed_deals', 'deals']
    
    for field in deal_fields:
        if field in restaurant and restaurant[field]:
            deal_text = str(restaurant[field])
            
            # Find all price matches in the deal text
            matches = re.findall(price_pattern, deal_text)
            
            for match in matches:
                try:
                    price = float(match)
                    # Only include reasonable prices (between 0.01 and 100)
                    if 0.01 <= price <= 100:
                        prices.append(price)
                except (ValueError, TypeError):
                    continue
    
    return prices if prices else []

def extract_price_from_deals(restaurant):
    """
    Extract the minimum price from deals text.
    
    Args:
        restaurant: Restaurant dictionary
        
    Returns:
        float: Minimum price found in deals, or float('inf') if no price found
    """
    prices = extract_all_prices_from_deals(restaurant)
    return min(prices) if prices else float('inf')

def display_filters(restaurants):
    """
    Display filter controls for restaurants in the sidebar.
    
    Args:
        restaurants: List of restaurant dictionaries
        
    Returns:
        tuple: (filtered_restaurants, distance_filter, min_rating, min_reviews, sort_by, sort_order, name_filter, deals_filter, max_price)
    """
    if not restaurants:
        return [], 0, 0, "Distance", "Descending", "", "", 100
    
    # Add a header to the sidebar
    st.sidebar.header("Filters")
    
    # Filter by restaurant name
    name_filter = st.sidebar.text_input("Filter by restaurant name", placeholder="Search restaurant names...")
    
    # Filter by deals
    deals_filter = st.sidebar.text_input("Filter by deals", placeholder="Search deals...")
    
    # Max Deal Price
    max_price = st.sidebar.number_input(
        "Max Deal Price ($)",
        min_value=0,
        max_value=100,
        value=100,
        step=5
    )
    
    # Min Reviews
    # Get all review counts, ensuring they are integers
    review_counts = [int(r.get('review_count', 0)) for r in restaurants]
    max_reviews = max(review_counts) if review_counts else 100
    
    min_reviews = st.sidebar.slider(
        "Min Reviews",
        0, max_reviews, 0, 50
    )
    
    # Min Rating
    min_rating = st.sidebar.slider(
        "Min Rating",
        0.0, 10.0, 0.0, 0.5
    )
    
    # Sort by option
    sort_by = st.sidebar.selectbox(
        "Sort By",
        ["Distance", "Rating", "Review Count", "Price"]
    )
    
    # Sort order option
    sort_order = st.sidebar.radio(
        "Sort Order",
        ["Ascending", "Descending"],
        horizontal=True
    )
    
    # Add a separator in the sidebar
    st.sidebar.markdown("---")
    
    # Apply filters and sorting
    filtered_restaurants = apply_filters_and_sorting(
        restaurants, min_rating, min_reviews, sort_by, sort_order, name_filter, deals_filter, max_price
    )
    
    # Show how many restaurants match the filters
    st.subheader(f"Found {len(filtered_restaurants)} restaurants")
    
    return filtered_restaurants, min_rating, min_reviews, sort_by, sort_order, name_filter, deals_filter, max_price

def apply_filters_and_sorting(restaurants, min_rating, min_reviews, sort_by, sort_order, name_filter="", deals_filter="", max_price=100):
    """
    Apply filters and sorting to the restaurant list.
    
    Args:
        restaurants: List of restaurant dictionaries
        min_rating: Minimum rating (0-10)
        min_reviews: Minimum number of reviews
        sort_by: Field to sort by ("Distance", "Rating", "Review Count", or "Price")
        sort_order: Sort order ("Ascending" or "Descending")
        name_filter: Text to filter restaurant names by
        deals_filter: Text to filter deals by
        max_price: Maximum price in deals
        
    Returns:
        list: Filtered and sorted list of restaurants
    """
    if not restaurants:
        return []
    
    # Normalize min_rating from 0-10 scale to 0-5 scale used internally
    normalized_min_rating = min_rating / 2  # Convert from 0-10 scale to 0-5 scale
    
    # Apply review filters with safe access
    filtered = [r for r in restaurants if r.get('rating', 0) >= normalized_min_rating and int(r.get('review_count', 0)) >= min_reviews]
    
    # Apply name filter if provided
    if name_filter:
        name_filter = name_filter.lower()
        filtered = [r for r in filtered if 'name' in r and r['name'] and name_filter in r['name'].lower()]
    
    # Apply deals filter if provided
    if deals_filter:
        deals_filter = deals_filter.lower()
        filtered_by_deals = []
        
        for restaurant in filtered:
            # Check for matches in different deal structures
            deal_match = False
            
            # Check new deal structure (summarized_deals and detailed_deals)
            if 'summarized_deals' in restaurant and restaurant['summarized_deals']:
                if deals_filter in restaurant['summarized_deals'].lower():
                    deal_match = True
            
            if not deal_match and 'detailed_deals' in restaurant and restaurant['detailed_deals']:
                if deals_filter in restaurant['detailed_deals'].lower():
                    deal_match = True
            
            # Check legacy deal structure
            if not deal_match and 'deals' in restaurant and restaurant['deals']:
                if deals_filter in restaurant['deals'].lower():
                    deal_match = True
                    
            # Include restaurant if any match found
            if deal_match:
                filtered_by_deals.append(restaurant)
        
        filtered = filtered_by_deals
    
    # Apply price filter if provided
    if max_price < 100:  # Only apply if not the default value
        price_filtered = []
        for r in filtered:
            # Extract all prices from the restaurant's deals
            prices = extract_all_prices_from_deals(r)
            
            # Include the restaurant if any of its prices are less than or equal to max_price
            if any(price <= max_price for price in prices):
                price_filtered.append(r)
                
        filtered = price_filtered
    
    # Apply sorting with safe access
    if sort_by == "Distance":
        filtered.sort(key=lambda r: get_distance_value(r), reverse=(sort_order == "Descending"))
    elif sort_by == "Rating":
        filtered.sort(key=lambda r: r.get('rating', 0), reverse=(sort_order == "Descending"))
    elif sort_by == "Review Count":
        filtered.sort(key=lambda r: int(r.get('review_count', 0)), reverse=(sort_order == "Descending"))
    elif sort_by == "Price":
        filtered.sort(key=lambda r: extract_price_from_deals(r), reverse=(sort_order == "Descending"))
    
    return filtered
