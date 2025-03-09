"""
Admin page component for the Pronto application.
Allows admin users to insert new rows into database tables.
"""
import streamlit as st
from utils.auth_utils import is_admin

# Import admin components
from ui.admin_display.components.user_management import manage_users
from ui.admin_display.components.restaurant_management import manage_restaurants
from ui.admin_display.components.deals_management import manage_deals
from ui.admin_display.components.categories_management import manage_categories
from ui.admin_display.components.restaurant_categories_management import manage_restaurant_categories
from ui.admin_display.components.role_management import manage_roles

def display_admin_page():
    """
    Display the admin page for database management.
    Only accessible to authenticated admin users.
    
    Returns:
        bool: True if the user should see the main content, False otherwise
    """
    # Check if user is authenticated and is an admin
    if not st.session_state.get('authenticated', False):
        st.error("You must be logged in to access this page.")
        return False
    
    username = st.session_state.get('username')
    if not username or not is_admin(username):
        st.error("You do not have permission to access this page.")
        return False
    
    # Add a "Back to Main" button at the top
    if st.button("← Back to Main", key="back_to_main_from_admin"):
        st.session_state.page = "main"
        st.rerun()
    
    # Display admin interface
    st.title("🔐 Admin Dashboard")
    st.write(f"Welcome, {username}! You have admin privileges.")
    
    # Create tabs for different tables
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "User Management", 
        "Restaurants", 
        "Deals", 
        "Categories", 
        "Restaurant Categories",
        "Role Types"
    ])
    
    with tab1:
        manage_users()
    
    with tab2:
        manage_restaurants()
    
    with tab3:
        manage_deals()
        
    with tab4:
        manage_categories()
        
    with tab5:
        manage_restaurant_categories()
    
    with tab6:
        manage_roles()
    
    # Return False to indicate that the main app content should not be shown
    return False
