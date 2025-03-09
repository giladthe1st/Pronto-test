"""
Role management component for admin interface.
"""
import streamlit as st
from ui.admin_display.components.utils import display_data_table, get_table_data, insert_record

def manage_roles():
    """Display role management interface."""
    st.header("Role Types")
    
    # Get existing roles
    roles = get_table_data('RoleTypes')
    display_data_table(roles, "Existing Role Types")
    
    # Form to add a new role
    display_add_role_form()

def display_add_role_form():
    """Display form for adding a new role type."""
    with st.expander("Add New Role Type"):
        with st.form("add_role_form"):
            role_type = st.text_input("Role Name")
            
            submitted = st.form_submit_button("Add Role")
            if submitted:
                handle_role_submission(role_type)

def handle_role_submission(role_type):
    """
    Handle the submission of a new role form.
    
    Args:
        role_type: Name of the role type
    """
    if not role_type:
        st.error("Role name is required.")
        return
    
    # Create role data
    role_data = {
        "role_type": role_type
    }
    
    # Insert the role
    success, message = insert_record('RoleTypes', role_data)
    if success:
        st.success(f"Role {role_type} added successfully!")
        st.rerun()  # Refresh the page to show the new role
    else:
        st.error(message)
