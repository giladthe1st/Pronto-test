"""
Components for displaying restaurant information in the Pronto application.
"""
import os
import streamlit as st
from PIL import Image
from utils.restaurant_utils import calculate_distance
from utils.image_utils import download_google_drive_image

def apply_restaurant_styling():
    """Apply common CSS styling for restaurant display."""
    st.markdown("""
    <style>
    .restaurant-name {
        font-weight: bold;
        font-size: 1.1em;
    }
    .section-header {
        font-weight: bold;
        margin-bottom: 5px;
    }
    .vertical-spacer {
        height: 35px;
    }
    </style>
    """, unsafe_allow_html=True)

def display_restaurant_logo(restaurant_name, logo_url=None):
    """
    Display a restaurant logo or placeholder.
    
    Args:
        restaurant_name: Name of the restaurant
        logo_url: Optional URL to download logo from if not found locally
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
        st.image(img, use_container_width =False, width=140)
    else:
        # Attempt to download logo if we have a URL
        if logo_url:
            downloaded_path = download_google_drive_image(logo_url, restaurant_name)
            if downloaded_path:
                img = Image.open(downloaded_path)
                # Maintain aspect ratio but ensure consistent size
                img.thumbnail((140, 140), Image.LANCZOS)
                st.image(img, use_container_width =False, width=140)
            else:
                st.markdown('<span style="font-size: 80px; color: #666;">🍽️</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span style="font-size: 80px; color: #666;">🍽️</span>', unsafe_allow_html=True)

def check_flyer_existence(restaurant_name):
    """
    Check if a flyer exists for a restaurant.
    
    Args:
        restaurant_name: Name of the restaurant
        
    Returns:
        tuple: (bool indicating if flyer exists, path to flyer)
    """
    flyer_path = f"flyers/{restaurant_name.lower().replace(' ', '_')}_flyer.jpg"
    return os.path.exists(flyer_path), flyer_path

def display_deal_section(restaurant, flyer_existence, text_filter=""):
    """
    Display the deal section for a restaurant.
    
    Args:
        restaurant: Dictionary containing restaurant information
        flyer_existence: Dictionary of pre-checked flyer existence by restaurant name
        text_filter: Text to filter deals by
    """
    st.markdown("<div class='section-header'>Deal</div>", unsafe_allow_html=True)
    
    # Check if a flyer exists for this restaurant (use pre-loaded check)
    has_flyer = flyer_existence[restaurant['name']]
    flyer_path = f"flyers/{restaurant['name'].lower().replace(' ', '_')}_flyer.jpg"
    
    # Check for new column structure first (summarized_deals and detailed_deals)
    if _has_detailed_deals(restaurant):
        _display_detailed_deals(restaurant, has_flyer, flyer_path, text_filter)
    # Fall back to legacy 'deals' column if new structure isn't available
    elif _has_legacy_deals(restaurant):
        _display_legacy_deals(restaurant, has_flyer, flyer_path, text_filter)
    else:
        # No deals available
        st.markdown("<em>No deals available</em>", unsafe_allow_html=True)

def _has_detailed_deals(restaurant):
    """Check if restaurant has detailed deals structure."""
    return ('summarized_deals' in restaurant and restaurant['summarized_deals'] and 
            'detailed_deals' in restaurant and restaurant['detailed_deals'])

def _has_legacy_deals(restaurant):
    """Check if restaurant has legacy deals structure."""
    return 'deals' in restaurant and restaurant['deals']

def _display_detailed_deals(restaurant, has_flyer, flyer_path, text_filter=""):
    """Display deals using the detailed deals structure."""
    summarized_deals = restaurant['summarized_deals']
    detailed_deals = restaurant['detailed_deals']
    
    # Split the deals
    summarized_list = [deal.strip() for deal in summarized_deals.split('->') if deal.strip()]
    detailed_list = [deal.strip() for deal in detailed_deals.split('->') if deal.strip()]
    
    # Make sure we have matching lists (or handle mismatches)
    if len(summarized_list) != len(detailed_list):
        # If lengths don't match, use the shorter length to avoid index errors
        min_length = min(len(summarized_list), len(detailed_list))
        summarized_list = summarized_list[:min_length]
        detailed_list = detailed_list[:min_length]
    
    # Filter deals based on text_filter if provided
    filtered_deals = _filter_detailed_deals(summarized_list, detailed_list, text_filter)
    
    # If we have filtered deals, display them
    if filtered_deals:
        _render_detailed_deals(restaurant, filtered_deals, has_flyer, flyer_path)
    else:
        # No deals match the filter
        _show_no_deals_message(text_filter)

def _filter_detailed_deals(summarized_list, detailed_list, text_filter=""):
    """Filter deals based on text filter."""
    if text_filter:
        text_filter = text_filter.lower()
        return [(i, summary, detail) for i, (summary, detail) in enumerate(zip(summarized_list, detailed_list))
                if text_filter in summary.lower() or text_filter in detail.lower()]
    else:
        # If no text filter, use all deals
        return [(i, summary, detail) for i, (summary, detail) in enumerate(zip(summarized_list, detailed_list))]

def _render_detailed_deals(restaurant, filtered_deals, has_flyer, flyer_path):
    """Render the detailed deals UI."""
    for i, summary, detail in filtered_deals:
        # Create a unique key for this specific deal
        deal_key = f"deal_{restaurant['name'].lower().replace(' ', '_')}_{i}"
        
        # Initialize this deal in session state if not already present
        if deal_key not in st.session_state:
            st.session_state[deal_key] = False
        
        # Create a clickable deal with fire emoji
        if st.button(f"🔥 {summary}", key=f"deal_btn_{deal_key}", use_container_width=True):
            st.session_state[deal_key] = not st.session_state[deal_key]
        
        # If this deal is expanded, show its detailed description
        if st.session_state[deal_key]:
            st.markdown(
                f"""
                <div style="margin-left: 25px; padding: 10px; background-color: #f9f9f9; 
                     border-left: 3px solid #ff4b4b; margin-bottom: 10px;">
                    <div style="color: #555; font-size: 0.9em;">Details:</div>
                    <div>{detail}</div>
                </div>
                """, 
                unsafe_allow_html=True
            )
    
    # Display flyer if available (below all deals)
    if has_flyer and any(st.session_state.get(f"deal_{restaurant['name'].lower().replace(' ', '_')}_{i}", False) 
                         for i, _, _ in filtered_deals):
        st.image(flyer_path, caption="Promotional Flyer", use_container_width =True)

def _display_legacy_deals(restaurant, has_flyer, flyer_path, text_filter=""):
    """Display deals using the legacy deals structure."""
    deals_text = restaurant['deals']
    
    # Split deals by the separator
    if '->' in deals_text:
        _display_multiple_legacy_deals(restaurant, deals_text, has_flyer, flyer_path, text_filter)
    else:
        _display_single_legacy_deal(restaurant, deals_text, has_flyer, flyer_path, text_filter)

def _display_multiple_legacy_deals(restaurant, deals_text, has_flyer, flyer_path, text_filter=""):
    """Display multiple legacy deals."""
    deals_list = [deal.strip() for deal in deals_text.split('->')]
    
    # Filter deals based on text_filter if provided
    filtered_deals = _filter_legacy_deals(deals_list, text_filter)
    
    # If we have filtered deals, display them
    if filtered_deals:
        _render_legacy_deals(restaurant, filtered_deals, has_flyer, flyer_path)
    else:
        # No deals match the filter
        _show_no_deals_message(text_filter)

def _filter_legacy_deals(deals_list, text_filter=""):
    """Filter legacy deals based on text filter."""
    if text_filter:
        text_filter = text_filter.lower()
        return [(i, deal) for i, deal in enumerate(deals_list) if text_filter in deal.lower()]
    else:
        # If no text filter, use all deals
        return [(i, deal) for i, deal in enumerate(deals_list)]

def _render_legacy_deals(restaurant, filtered_deals, has_flyer, flyer_path):
    """Render the legacy deals UI."""
    for i, deal in filtered_deals:
        # Create a unique key for this specific deal
        deal_key = f"deal_{restaurant['name'].lower().replace(' ', '_')}_{i}"
        
        # Initialize this deal in session state if not already present
        if deal_key not in st.session_state:
            st.session_state[deal_key] = False
        
        # Create a clickable deal with fire emoji
        if st.button(f"🔥 {deal}", key=f"deal_btn_{deal_key}", use_container_width=True):
            st.session_state[deal_key] = not st.session_state[deal_key]
        
        # No detailed version available in legacy format, so just highlight when clicked
        if st.session_state[deal_key]:
            st.markdown(
                f"""
                <div style="margin-left: 25px; padding: 10px; background-color: #f9f9f9; 
                     border-left: 3px solid #ff4b4b; margin-bottom: 10px;">
                    {deal}
                </div>
                """, 
                unsafe_allow_html=True
            )
    
    # Display flyer if available (below all deals)
    if has_flyer and any(st.session_state.get(f"deal_{restaurant['name'].lower().replace(' ', '_')}_{i}", False) 
                         for i, _ in filtered_deals):
        st.image(flyer_path, caption="Promotional Flyer", use_container_width =True)

def _display_single_legacy_deal(restaurant, deals_text, has_flyer, flyer_path, text_filter=""):
    """Display a single legacy deal."""
    deal_key = f"deal_{restaurant['name'].lower().replace(' ', '_')}_0"
    
    # Check if the single deal matches the text filter
    show_deal = True
    if text_filter and text_filter.lower() not in deals_text.lower():
        show_deal = False
    
    if show_deal:
        # Initialize this deal in session state if not already present
        if deal_key not in st.session_state:
            st.session_state[deal_key] = False
        
        # Create a clickable deal with fire emoji
        if st.button(f"🔥 {deals_text}", key=f"deal_btn_{deal_key}", use_container_width=True):
            st.session_state[deal_key] = not st.session_state[deal_key]
        
        # Show expanded content if clicked
        if st.session_state[deal_key]:
            st.markdown(
                f"""
                <div style="margin-left: 25px; padding: 10px; background-color: #f9f9f9; 
                     border-left: 3px solid #ff4b4b; margin-bottom: 10px;">
                    {deals_text}
                </div>
                """, 
                unsafe_allow_html=True
            )
            
            # Display flyer if available
            if has_flyer:
                st.image(flyer_path, caption="Promotional Flyer", use_container_width =True)
    else:
        # No deals match the filter
        _show_no_deals_message(text_filter)

def _show_no_deals_message(text_filter=""):
    """Show message when no deals are available or match the filter."""
    if text_filter:
        st.markdown(f"<em>No deals matching '{text_filter}'</em>", unsafe_allow_html=True)
    else:
        st.markdown("<em>No deals available</em>", unsafe_allow_html=True)

def display_menu_section(restaurant):
    """
    Display the menu section for a restaurant.
    
    Args:
        restaurant: Dictionary containing restaurant information
    """
    st.markdown("<div class='section-header'>Menu</div>", unsafe_allow_html=True)
    
    # Create a unique key for this restaurant's menu expander
    menu_key = f"menu_{restaurant['name'].lower().replace(' ', '_')}"
    
    # Initialize this menu in session state if not already present
    if menu_key not in st.session_state:
        st.session_state[menu_key] = False
    
    # Create a toggle function for this menu with proper closure
    def toggle_menu(key=menu_key):
        st.session_state[key] = not st.session_state[key]
    
    # Create an expandable menu section with toggle button
    button_text = "View Menu"
    if st.session_state[menu_key]:
        button_text = "Hide Menu"
    
    # Use a more efficient button implementation with a different key for the button
    st.button(
        button_text, 
        key=f"btn_{menu_key}", 
        help="Click to expand/collapse", 
        on_click=toggle_menu,
        use_container_width=True
    )
    
    # Show expanded content if this menu is expanded
    if st.session_state[menu_key]:
        st.markdown("<div class='expanded-content'>", unsafe_allow_html=True)
        st.markdown("<strong>Menu Information:</strong>", unsafe_allow_html=True)
        st.markdown(f"<a href='{restaurant['menu_url']}' target='_blank'>Open Full Menu in New Tab</a>", unsafe_allow_html=True)
        
        # Use lazy loading for iframe to improve performance
        # Only load iframe when menu is expanded
        if 'menu_url' in restaurant and restaurant['menu_url']:
            st.components.v1.iframe(
                restaurant['menu_url'], 
                height=300, 
                scrolling=True
            )
        
        st.markdown("</div>", unsafe_allow_html=True)

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

def display_location_section(restaurant, user_location=None):
    """
    Display the location section for a restaurant.
    
    Args:
        restaurant: Dictionary containing restaurant information
        user_location: Dictionary containing user's latitude and longitude
    """
    st.markdown("<div class='section-header'>Location</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='restaurant-location'><strong>Address:</strong> {restaurant['location']}</div>", unsafe_allow_html=True)
    
    # Calculate and display distance if we have both user location and restaurant coordinates
    has_user_location = user_location and user_location['latitude'] is not None and user_location['longitude'] is not None
    has_restaurant_coords = 'latitude' in restaurant and 'longitude' in restaurant
    
    if has_user_location and has_restaurant_coords:
        display_calculated_distance(restaurant, user_location)
    else:
        # Display default distance if we don't have coordinates
        st.markdown(f"<div class='restaurant-distance'><strong>Distance:</strong> {restaurant.get('distance', 'Unknown')}</div>", unsafe_allow_html=True)
    
    # Display Google Maps link
    st.markdown(f"<div class='restaurant-info'><a href='{restaurant['maps_url']}' target='_blank'>📍 Get Directions</a></div>", unsafe_allow_html=True)

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
