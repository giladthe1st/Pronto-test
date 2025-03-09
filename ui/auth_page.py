"""
Authentication page components for the Pronto application.
"""
import streamlit as st
from utils.auth_utils import (
    authenticate_user, 
    register_user,
    is_admin
)

def initialize_auth_state():
    """Initialize authentication state in session state if not already present."""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'auth_page' not in st.session_state:
        st.session_state.auth_page = "main"  # Options: "main", "login", "register"
    if 'success_message' not in st.session_state:
        st.session_state.success_message = ""
    if 'page' not in st.session_state:
        st.session_state.page = "main"  # Options: "main", "admin"

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

def register_callback():
    """Callback function for registration form submission."""
    email = st.session_state.register_email
    password = st.session_state.register_password
    confirm_password = st.session_state.register_confirm_password
    
    # Validate input
    if not email or not password:
        st.error("All fields are required")
        return
    
    if password != confirm_password:
        st.error("Passwords do not match")
        return
    
    # Register the user
    if register_user(password, email):
        st.session_state.auth_page = "login"
        st.success("Registration successful! Please log in.")
    else:
        st.error("Registration failed. Email may already exist.")

def logout():
    """Log out the current user."""
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.page = "main"  # Reset to main page

def display_auth_button():
    """Display login/register/logout buttons in the top right corner."""
    # Create a container for the buttons
    with st.container():
        if st.session_state.authenticated:
            # Show username/logout button when authenticated
            if is_admin(st.session_state.username):
                # For admin users, show admin dashboard button and logout
                col1, col2, col3 = st.columns([8, 1, 1])
                with col2:
                    st.button("Admin Dashboard", key="admin_button", type="secondary", on_click=set_page, args=("admin",))
                with col3:
                    st.button(f"👤 {st.session_state.username}", key="auth_button", type="secondary", on_click=logout)
            else:
                # For regular users, just show username/logout
                col1, col2 = st.columns([9, 1])
                with col2:
                    st.button(f"👤 {st.session_state.username}", key="auth_button", type="secondary", on_click=logout)
        else:
            # Show login/register buttons when not authenticated
            col1, col2 = st.columns([9, 1])
            with col2:
                # Use columns to place buttons side by side with no gap
                bcol1, bcol2 = st.columns([1, 1])
                with bcol1:
                    st.button("Register", key="register_button", type="secondary", on_click=set_auth_page, args=("register",))
                with bcol2:
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
        
        col1, col2 = st.columns([1, 1])
        with col1:
            st.form_submit_button("Login", on_click=login_callback)
        with col2:
            st.form_submit_button("Register Instead", on_click=set_auth_page, args=("register",))

def display_register_page():
    """Display the registration page."""
    st.title("Register")
    
    # Back button
    st.button("← Back to Main", key="back_to_main_register", on_click=set_auth_page, args=("main",))
    
    with st.form("register_form"):
        st.text_input("Email", key="register_email")
        st.text_input("Password", type="password", key="register_password")
        st.text_input("Confirm Password", type="password", key="register_confirm_password")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            st.form_submit_button("Register", on_click=register_callback)
        with col2:
            st.form_submit_button("Login Instead", on_click=set_auth_page, args=("login",))

def display_auth_page():
    """Display the authentication components and check if user is authenticated."""
    # Initialize authentication state
    initialize_auth_state()
    
    # Display the appropriate page based on auth_page state
    if st.session_state.auth_page == "login":
        display_login_page()
        return False  # Don't display main content
    elif st.session_state.auth_page == "register":
        display_register_page()
        return False  # Don't display main content
    else:
        # Display the login/register/logout buttons
        display_auth_button()
        # Return authentication status for the main page
        return True  # Always show main content for the main page
