"""
Authentication page components for the Pronto application.
"""
import streamlit as st
from utils.auth_utils import (
    authenticate_user, 
    is_admin
)

def initialize_auth_state():
    """Initialize authentication state in session state if not already present."""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'auth_page' not in st.session_state:
        st.session_state.auth_page = "main"  # Options: "main", "login"
    if 'success_message' not in st.session_state:
        st.session_state.success_message = ""

def set_auth_page(page):
    """Set the authentication page."""
    st.session_state.auth_page = page

def set_page(page):
    """Set the application page."""
    st.session_state.page = page

def login_callback():
    """Callback function for login form submission."""
    email = st.session_state.login_email
    password = st.session_state.login_password
    
    # Try regular authentication
    auth_result = authenticate_user(email, password)
    
    if auth_result:
        st.session_state.authenticated = True
        st.session_state.username = email
        st.session_state.auth_page = "main"
        st.session_state.success_message = f"Welcome back, {email}!"
    else:
        st.error("Invalid username or password")

def logout():
    """Log out the current user."""
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.page = "main"  # Reset to main page

def display_auth_button():
    """Display login/logout buttons in the top right corner."""
    # Create a container for the buttons
    with st.container():
        if st.session_state.authenticated:
            # Show username and logout button when authenticated
            if is_admin(st.session_state.username):
                # For admin users, create a cleaner layout
                col1, col2 = st.columns([8, 2])
                with col2:
                    # Create a container with a light background for the user info
                    with st.container():
                        st.write("Admin")
                        st.button("Dashboard", key="admin_button", type="secondary", on_click=set_page, args=("admin",))
                        st.write(f"👤 {st.session_state.username}")
                        st.button("Logout", key="logout_button", type="secondary", on_click=logout)
            else:
                # For regular users, create a cleaner layout
                col1, col2 = st.columns([8, 2])
                with col2:
                    # Create a container with a light background for the user info
                    with st.container():
                        st.write(f"👤 {st.session_state.username}")
                        st.button("Logout", key="logout_button", type="secondary", on_click=logout)
        else:
            # Show login button when not authenticated
            col1, col2 = st.columns([9, 1])
            with col2:
                st.button("Login", key="login_button", type="secondary", on_click=set_auth_page, args=("login",))
    
    # Show success message if needed
    if st.session_state.success_message:
        st.success(st.session_state.success_message)
        st.session_state.success_message = ""

def display_login_page():
    """Display the login page."""
    st.title("Login")
    
    # Back button
    st.button("← Back to Main", key="back_to_main_login", on_click=set_auth_page, args=("main",))
    
    with st.form("login_form"):
        st.text_input("Email", key="login_email")
        st.text_input("Password", type="password", key="login_password")
        st.form_submit_button("Login", on_click=login_callback)

def display_auth_page() -> bool:
    """Main authentication page handler."""
    # Ensure auth state is initialized
    initialize_auth_state()
    
    # Check auth page state (now guaranteed to exist)
    current_auth_page = st.session_state.auth_page
    
    if current_auth_page == "login":
        display_login_page()
        return False
    
    display_auth_button()
    return True
