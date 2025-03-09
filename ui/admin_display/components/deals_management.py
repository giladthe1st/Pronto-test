"""
Deals management component for admin interface.
"""
import streamlit as st
from ui.admin_display.components.utils import display_data_table, get_table_data, get_dropdown_options, insert_record

def manage_deals():
    """Display deals management interface."""
    st.header("Deals")
    
    # Get existing deals
    deals = get_table_data('Deals')
    display_data_table(deals, "Existing Deals")
    
    # Get restaurants for the dropdown
    restaurant_options = get_dropdown_options('Restaurants', 'id', 'name')
    
    # Form to add a new deal
    display_add_deal_form(restaurant_options)

def display_add_deal_form(restaurant_options):
    """
    Display form for adding a new deal.
    
    Args:
        restaurant_options (dict): Dictionary of restaurant names to ids
    """
    with st.expander("Add New Deal"):
        with st.form("add_deal_form"):
            if restaurant_options:
                selected_restaurant = st.selectbox("Restaurant", list(restaurant_options.keys()))
                restaurant_id = restaurant_options[selected_restaurant]
            else:
                st.warning("No restaurants available. Please add restaurants first.")
                selected_restaurant = None
                restaurant_id = None
            
            details = st.text_area("Deal Details")
            summarized_deal = st.text_input("Summarized Deal")
            price = st.number_input("Price", min_value=0.0, step=0.01)
            
            submitted = st.form_submit_button("Add Deal")
            if submitted:
                handle_deal_submission(restaurant_id, selected_restaurant, details, summarized_deal, price)

def handle_deal_submission(restaurant_id, selected_restaurant, details, summarized_deal, price):
    """
    Handle the submission of a new deal form.
    
    Args:
        restaurant_id: ID of the selected restaurant
        selected_restaurant: Name of the selected restaurant (for display)
        details: Deal details
        summarized_deal: Summarized deal text
        price: Deal price
    """
    if not restaurant_id:
        st.error("Please add restaurants first.")
        return
        
    if not details or not summarized_deal:
        st.error("Deal details and summary are required.")
        return
    
    # Create deal data
    deal_data = {
        "restaurant_id": restaurant_id,
        "restaurant_name": selected_restaurant,  
        "details": details,
        "summarized_deal": summarized_deal,
        "price": price
    }
    
    # Insert the deal
    success, message = insert_record('Deals', deal_data)
    if success:
        st.success(f"Deal for {selected_restaurant} added successfully!")
        st.rerun()  # Refresh the page
    else:
        st.error(message)
