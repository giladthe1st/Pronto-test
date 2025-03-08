import streamlit as st
from utils.image_utils import ensure_directories_exist, clean_cache_directory
from utils.restaurant_utils import download_google_sheet_data, process_restaurant_data, get_user_location_from_ip, calculate_distance
from ui.restaurant_display import display_restaurants
from ui.filters import display_filters
from utils.startup_utils import clear_data_on_startup
import os

# Set page configuration to wide mode
st.set_page_config(layout="wide")

def main():
    """Main application entry point"""
    # Clear data only on server startup (not on page refreshes)
    clear_data_on_startup()
    
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
    
    # Ensure directories exist at startup
    ensure_directories_exist()
    
    # Ensure logo_images directory exists
    logo_images_dir = 'logo_images'
    if not os.path.exists(logo_images_dir):
        os.makedirs(logo_images_dir)
    
    # Clean cache on startup
    clean_cache_directory()
    
    # Download/load Google Sheet data
    df = download_google_sheet_data()
    
    # Process the data with caching
    restaurants = process_restaurant_data(df)
    
    if not restaurants:
        st.error("No data available. Please check your Google Sheets connection.")
        return
    
    # Pre-calculate distances for all restaurants before filtering
    user_location = st.session_state.user_location
    for restaurant in restaurants:
        has_user_location = user_location and user_location['latitude'] is not None and user_location['longitude'] is not None
        has_restaurant_coords = 'latitude' in restaurant and 'longitude' in restaurant
        
        if has_user_location and has_restaurant_coords:
            # Calculate distance using the Haversine formula
            distance_km = calculate_distance(
                user_location['latitude'], 
                user_location['longitude'],
                restaurant['latitude'], 
                restaurant['longitude']
            )
            
            # Convert to miles
            distance_mi = distance_km * 0.621371
            
            # Store the formatted distance for filtering
            if distance_mi < 0.1:
                restaurant['distance'] = "0.1 mi"
            else:
                restaurant['distance'] = f"{distance_mi:.1f} mi"
    
    # Display filters and get filtered restaurants
    filtered_restaurants, *_, text_filter = display_filters(restaurants)
    
    # Pre-load flyer existence checks to avoid repeated file system operations
    flyer_existence = {}
    for restaurant in filtered_restaurants:
        flyer_path = f"flyers/{restaurant['name'].lower().replace(' ', '_')}_flyer.jpg"
        flyer_existence[restaurant['name']] = os.path.exists(flyer_path)
    
    # Display restaurants with user's actual location and text filter
    display_restaurants(filtered_restaurants, flyer_existence, st.session_state.user_location, text_filter)

if __name__ == "__main__":
    main()