"""
Restaurant management component for admin interface.
"""
import streamlit as st
from ui.admin_display.components.utils import display_data_table, get_table_data, insert_record

def manage_restaurants():
    """Display restaurant data management interface."""
    st.header("Restaurants")
    
    # Get existing restaurants
    restaurants = get_table_data('Restaurants')
    display_data_table(restaurants, "Existing Restaurants")
    
    # Form to add a new restaurant
    display_add_restaurant_form()

def display_add_restaurant_form():
    """Display form for adding a new restaurant."""
    with st.expander("Add New Restaurant"):
        with st.form("add_restaurant_form"):
            name = st.text_input("Restaurant Name")
            address = st.text_input("Address")
            logo_url = st.text_input("Logo URL")
            website_url = st.text_input("Website URL")
            reviews_count = st.number_input("Reviews Count", min_value=0, step=1)
            average_rating = st.number_input("Average Rating", min_value=0.0, max_value=10.0, step=0.1)
            maps_url = st.text_input("Google Maps URL")
            
            submitted = st.form_submit_button("Add Restaurant")
            if submitted:
                handle_restaurant_submission(name, address, logo_url, website_url, 
                                           reviews_count, average_rating, maps_url)

def handle_restaurant_submission(name, address, logo_url, website_url, 
                               reviews_count, average_rating, maps_url):
    """Handle the submission of a new restaurant form."""
    if not name or not address:
        st.error("Restaurant name and address are required.")
        return
    
    # Create restaurant data
    restaurant_data = {
        "name": name,
        "address": address,
        "logo_url": logo_url,
        "website_url": website_url,
        "reviews_count": reviews_count,
        "average_rating": average_rating,
        "maps_url": maps_url
    }
    
    # Insert the restaurant
    success, message = insert_record('Restaurants', restaurant_data)
    if success:
        st.success(f"Restaurant {name} added successfully!")
        st.rerun()  # Refresh the page
    else:
        st.error(message)
