import streamlit as st
from PIL import Image
import requests
from io import BytesIO
import os
import re
from data_handler import DataHandler

# Page configuration
st.set_page_config(
    page_title="Restaurant Finder",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="collapsed"  # Hide sidebar by default
)

# Custom CSS for better styling
def load_css(css_file):
    with open(css_file, 'r') as f:
        css = f.read()
    return st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

# Load external CSS
load_css('static/styles.css')

def load_image_from_url(url_or_path):
    """Load an image from a URL or local file path."""
    try:
        # Check if it's a URL or local path
        if url_or_path.startswith(('http://', 'https://')):
            # It's a URL
            response = requests.get(url_or_path)
            img = Image.open(BytesIO(response.content))
        else:
            # It's a local path
            img = Image.open(url_or_path)
        return img
    except Exception as e:
        st.warning(f"Could not load image from {url_or_path}: {e}")
        # Return a placeholder image
        return None

def parse_reviews(review_str):
    """
    Parse the reviews string to extract rating and count
    Example format: "4.5/5 (120 reviews)"
    Returns: (rating, count)
    """
    try:
        # Extract rating (e.g., 4.5 from "4.5/5")
        rating_match = re.search(r'(\d+\.\d+|\d+)\/\d+', review_str)
        rating = float(rating_match.group(1)) if rating_match else 0.0
        
        # Extract count (e.g., 120 from "(120 reviews)")
        count_match = re.search(r'\((\d+)\s+reviews\)', review_str)
        count = int(count_match.group(1)) if count_match else 0
        
        return rating, count
    except Exception:
        return 0.0, 0

def main():
    st.title("🍽️ Pronto")
    
    # Initialize session state for tracking expanded/collapsed states
    if 'expanded_deals' not in st.session_state:
        st.session_state.expanded_deals = {}
    
    if 'expanded_menus' not in st.session_state:
        st.session_state.expanded_menus = {}
    
    # Load data
    restaurants = []
    csv_file = "sample_restaurants.csv"
    if os.path.exists(csv_file):
        df = DataHandler.load_from_csv(csv_file)
        restaurants = DataHandler.format_restaurant_data(df)
    else:
        st.error(f"CSV file not found: {csv_file}")
    
    # Pre-process reviews data for filtering
    if restaurants:
        # Extract rating and review count from the reviews string
        for restaurant in restaurants:
            rating, count = parse_reviews(restaurant['reviews'])
            restaurant['rating'] = rating
            restaurant['review_count'] = count
    
    # Admin section for uploading flyers (collapsible)
    with st.expander("🔧 Admin: Upload Flyers", expanded=False):
        st.markdown("### Upload Flyers for Restaurants")
        st.markdown("Select a restaurant and upload a flyer image. The flyer will be displayed when users click on the deal.")
        
        # Create a directory for flyers if it doesn't exist
        flyers_dir = "flyers"
        if not os.path.exists(flyers_dir):
            os.makedirs(flyers_dir)
        
        # Restaurant selection dropdown
        if restaurants:
            selected_restaurant = st.selectbox(
                "Select Restaurant",
                options=[r['name'] for r in restaurants]
            )
            
            # File uploader for flyer
            uploaded_flyer = st.file_uploader("Upload Flyer Image", type=["jpg", "jpeg", "png"])
            
            if uploaded_flyer is not None:
                # Save the uploaded flyer
                flyer_path = os.path.join(flyers_dir, f"{selected_restaurant.lower().replace(' ', '_')}_flyer.jpg")
                
                # Save the image
                with open(flyer_path, "wb") as f:
                    f.write(uploaded_flyer.getbuffer())
                
                st.success(f"Flyer uploaded successfully for {selected_restaurant}!")
                
                # Display the uploaded flyer
                st.image(uploaded_flyer, caption=f"Flyer for {selected_restaurant}", width=300)
    
    # Create 5 columns for filters in one line
    if restaurants:
        filter_col1, filter_col2, filter_col3, filter_col4, filter_col5 = st.columns(5)
        
        # Distance filter
        with filter_col1:
            max_distance = max([float(r['distance'].split()[0]) for r in restaurants])
            distance_filter = st.slider(
                "Max Distance (mi)",
                0.0, max_distance, max_distance, 0.1
            )
        
        # Rating filter
        with filter_col2:
            min_rating = st.slider(
                "Min Rating",
                0.0, 5.0, 0.0, 0.1
            )
        
        # Review count filter
        with filter_col3:
            min_reviews = st.slider(
                "Min Reviews",
                0, max([r['review_count'] for r in restaurants]) if restaurants else 100, 0
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
                ["Descending", "Ascending"],
                horizontal=True
            )
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Filter and sort the restaurants
    if restaurants:
        # Apply distance filter
        restaurants = [r for r in restaurants if float(r['distance'].split()[0]) <= distance_filter]
        
        # Apply review filters
        restaurants = [r for r in restaurants if r['rating'] >= min_rating and r['review_count'] >= min_reviews]
        
        # Apply sorting
        if sort_by == "Distance":
            restaurants.sort(key=lambda r: float(r['distance'].split()[0]), reverse=(sort_order == "Descending"))
        elif sort_by == "Rating":
            restaurants.sort(key=lambda r: r['rating'], reverse=(sort_order == "Descending"))
        elif sort_by == "Review Count":
            restaurants.sort(key=lambda r: r['review_count'], reverse=(sort_order == "Descending"))
    
    # Show how many restaurants match the filters
    st.subheader(f"Found {len(restaurants)} restaurants")
    
    # Display restaurants
    if not restaurants:
        st.info("No restaurants found. Please check your data source or adjust your filters.")
    else:
        for restaurant in restaurants:
            # Create a row for each restaurant
            with st.container():
                
                # Use 6 columns for better organization
                col1, col2, col3, col4, col5, col6 = st.columns([1, 1.5, 1, 1, 1.5, 1.5])
                
                # Column 1: Logo
                with col1:
                    img = load_image_from_url(restaurant['logo_url'])
                    if img:
                        # Resize image to fit better
                        img = img.resize((80, 80))
                        # Add a container div with style
                        st.markdown('<div style="display: flex; justify-content: center;">', unsafe_allow_html=True)
                        # Use st.image with supported parameters
                        st.image(img, width=80, output_format="JPEG", clamp=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.markdown("🍽️")
                
                # Column 2: Name
                with col2:
                    st.markdown(f"<div class='restaurant-name'><a href='{restaurant['website']}' target='_blank'>{restaurant['name']}</a></div>", unsafe_allow_html=True)
                
                # Column 3: Deals (now expandable)
                with col3:
                    st.markdown("<div class='section-header'>Deal</div>", unsafe_allow_html=True)
                    
                    # Create a unique key for this restaurant's deal expander
                    deal_key = f"deal_{restaurant['name'].lower().replace(' ', '_')}"
                    
                    # Check if a flyer exists for this restaurant
                    flyer_path = f"flyers/{restaurant['name'].lower().replace(' ', '_')}_flyer.jpg"
                    has_flyer = os.path.exists(flyer_path)
                    
                    # Initialize this deal in session state if not already present
                    if deal_key not in st.session_state.expanded_deals:
                        st.session_state.expanded_deals[deal_key] = False
                    
                    # Create a toggle function for this deal
                    def toggle_deal(deal_key=deal_key):
                        st.session_state.expanded_deals[deal_key] = not st.session_state.expanded_deals[deal_key]
                    
                    # Create an expandable deal section with toggle button
                    button_text = "🔥 " + restaurant['deals']
                    if st.session_state.expanded_deals[deal_key]:
                        button_text = "🔽 " + restaurant['deals']
                    
                    st.button(button_text, key=deal_key, help="Click to expand/collapse", on_click=toggle_deal)
                    
                    # Show expanded content if this deal is expanded
                    if st.session_state.expanded_deals[deal_key]:
                        st.markdown("<div class='expanded-content'>", unsafe_allow_html=True)
                        st.markdown(f"<strong>Deal Details:</strong> {restaurant['deals']}", unsafe_allow_html=True)
                        
                        # Display flyer if available
                        if has_flyer:
                            st.image(flyer_path, caption="Promotional Flyer", use_column_width=True)
                        else:
                            st.info("No flyer available for this deal.")
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                
                # Column 4: Menu (now expandable)
                with col4:
                    st.markdown("<div class='section-header'>Menu</div>", unsafe_allow_html=True)
                    
                    # Create a unique key for this restaurant's menu expander
                    menu_key = f"menu_{restaurant['name'].lower().replace(' ', '_')}"
                    
                    # Initialize this menu in session state if not already present
                    if menu_key not in st.session_state.expanded_menus:
                        st.session_state.expanded_menus[menu_key] = False
                    
                    # Create a toggle function for this menu
                    def toggle_menu(menu_key=menu_key):
                        st.session_state.expanded_menus[menu_key] = not st.session_state.expanded_menus[menu_key]
                    
                    # Create an expandable menu section with toggle button
                    button_text = "View Menu"
                    if st.session_state.expanded_menus[menu_key]:
                        button_text = "Hide Menu"
                    
                    st.button(button_text, key=menu_key, help="Click to expand/collapse", on_click=toggle_menu)
                    
                    # Show expanded content if this menu is expanded
                    if st.session_state.expanded_menus[menu_key]:
                        st.markdown("<div class='expanded-content'>", unsafe_allow_html=True)
                        st.markdown("<strong>Menu Information:</strong>", unsafe_allow_html=True)
                        st.markdown(f"<a href='{restaurant['menu_url']}' target='_blank'>Open Full Menu in New Tab</a>", unsafe_allow_html=True)
                        
                        # Display embedded menu if available (could be implemented with iframe)
                        st.components.v1.iframe(restaurant['menu_url'], height=300, scrolling=True)
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                
                # Column 5: Reviews
                with col5:
                    st.markdown("<div class='section-header'>Reviews</div>", unsafe_allow_html=True)
                    # Calculate stars based on rating
                    stars = "★" * int(restaurant['rating']) + "☆" * (5 - int(restaurant['rating']))
                    st.markdown(
                        f"<div class='restaurant-reviews'>"
                        f"<span class='stars'>{stars}</span> "
                        f"<span class='rating-text'>{restaurant['rating']}/5 ({restaurant['review_count']} reviews)</span>"
                        f"</div>", 
                        unsafe_allow_html=True
                    )
                
                # Column 6: Location, Distance, Maps
                with col6:
                    st.markdown("<div class='section-header'>Location</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='restaurant-location'><strong>Address:</strong> {restaurant['location']}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='restaurant-distance'><strong>Distance:</strong> {restaurant['distance']}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='restaurant-info'><a href='{restaurant['maps_url']}' target='_blank'>📍 Get Directions</a></div>", unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
