"""
User management component for admin interface.
"""
import streamlit as st
from utils.auth_utils import hash_password
from ui.admin_display.components.utils import display_data_table, get_table_data, get_dropdown_options, insert_record

def manage_users():
    """Display user management interface."""
    st.header("User Management")
    
    # Get all users
    users = get_table_data('Users')
    
    if users:
        # Hide password column for security
        for user in users:
            if 'password' in user:
                user['password'] = '********'
        
        display_data_table(users, "Existing Users")
    
    # Form to add a new user
    display_add_user_form()

def display_add_user_form():
    """Display form for adding a new user."""
    with st.expander("Add New User"):
        with st.form("add_user_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            
            # Get role types for dropdown
            role_options = get_dropdown_options('RoleTypes', 'id', 'role_type')
            
            if role_options:
                selected_role = st.selectbox("Role", list(role_options.keys()))
                role_id = role_options[selected_role]
            else:
                st.warning("No role types found. Please add role types first.")
                selected_role = None
                role_id = None
            
            submitted = st.form_submit_button("Add User")
            if submitted:
                handle_user_submission(email, password, selected_role, role_id)

def handle_user_submission(email, password, selected_role, role_id):
    """Handle the submission of a new user form."""
    if not email or not password:
        st.error("Email and password are required.")
        return
    
    if not role_id:
        st.error("Role selection is required.")
        return
    
    # Hash the password
    hashed_password = hash_password(password)
    
    # Create user data
    user_data = {
        "email": email,
        "password": hashed_password,
        "role": role_id
    }
    
    # Insert the user
    success, message = insert_record('Users', user_data)
    if success:
        st.success(f"User {email} added successfully!")
        st.rerun()  # Refresh the page to show the new user
    else:
        st.error(message)
