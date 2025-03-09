import streamlit as st
from utils.image_handler import ensure_cache_directory, ensure_directories_exist
from utils.location_utils import get_user_location_from_ip
from ui.restaurant_display.restaurant_display import display_restaurants
from ui.filters import display_filters
from utils.startup_utils import clear_data_on_startup
from ui.auth_page import display_auth_page, initialize_auth_state
from ui.admin_display.admin_page import display_admin_page
from utils.db_data_utils import load_restaurant_data_from_db, process_restaurant_locations
import os

# Set page configuration to wide mode
st.set_page_config(layout="wide")

def main():
    """Main application entry point"""
    # Clear data only on server startup (not on page refreshes)
    clear_data_on_startup()
    
    # Ensure directories exist at startup
    ensure_directories_exist()
    
    # Ensure image cache directory exists for the new image handler
    ensure_cache_directory()
    
    # Initialize authentication state
    initialize_auth_state()
    
    # Initialize page state if not already present
    if 'page' not in st.session_state:
        st.session_state.page = 'main'
    
    # Check if we're on the admin page
    if st.session_state.get('page') == 'admin':
        # Display admin page and check if we should show main content
        show_main_content = display_admin_page()
    else:
        # Display authentication pages or main app based on auth state
        # If display_auth_page returns False, we're on a dedicated auth page
        # and should not display the main app content
        show_main_content = display_auth_page()
    
    if show_main_content:
        # Display the main app content
        display_main_app()

def display_main_app():
    """Display the main application content."""
    st.title("🍽️ Pronto")
    
    # Initialize session state for tracking expanded/collapsed states
    if 'expanded_deals' not in st.session_state:
        st.session_state.expanded_deals = {}
    
    if 'expanded_menus' not in st.session_state:
        st.session_state.expanded_menus = {}
    
    # Initialize user location in session state if not already present
    if 'user_location' not in st.session_state:
        # Get the user's location based on their IP address
        st.session_state.user_location = get_user_location_from_ip()
    
    # Display user location at the top of the page
    col1, col2 = st.columns([3, 1])
    with col2:
        st.markdown(f"<div style='text-align: right; padding: 10px; background-color: #f0f2f6; border-radius: 5px;'><strong>My Location:</strong> {st.session_state.user_location['address']}</div>", unsafe_allow_html=True)
    
    # Load restaurant data from database
    restaurants = load_restaurant_data_from_db()
    
    if not restaurants:
        st.error("No data available. Please check your database connection.")
        return
    
    # Process restaurant locations and calculate distances
    restaurants = process_restaurant_locations(restaurants)
    
    # Display filters and get filtered restaurants
    filtered_restaurants, min_rating, min_reviews, sort_by, sort_order, name_filter, deals_filter, max_price = display_filters(restaurants)
    
    # Pre-load flyer existence checks to avoid repeated file system operations
    flyer_existence = {}
    for restaurant in filtered_restaurants:
        flyer_path = f"flyers/{restaurant['name'].lower().replace(' ', '_')}_flyer.jpg"
        flyer_existence[restaurant['name']] = os.path.exists(flyer_path)
    
    # Display restaurants with user's actual location and text filter
    display_restaurants(filtered_restaurants, flyer_existence, st.session_state.user_location, deals_filter)

if __name__ == "__main__":
    main()