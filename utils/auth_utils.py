"""
Utility functions for user authentication in the Pronto application.
"""
import hashlib
import streamlit as st
from typing import Dict, Optional, List
from database.supabase_client import (
    user_exists,
    create_user as supabase_create_user,
    get_user,
    update_user,
    get_favorites as supabase_get_favorites,
    add_favorite as supabase_add_favorite,
    get_role_id,
    get_role_name
)

def hash_password(password: str) -> str:
    """
    Hash a password for secure storage.
    
    Args:
        password: The plain text password to hash
        
    Returns:
        Hashed password
    """
    # Simple hash for now - in a real application, you'd want to use a more secure method
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(password: str, email: str, role: str = "User") -> bool:
    """
    Register a new user.
    
    Args:
        password: Password for the new user
        password: Password for the new user
        email: Email for the new user
        role: Role for the new user (default: "User")
        
    Returns:
        True if registration successful, False otherwise
    """
    # Check if email already exists
    if user_exists(email):
        st.error("Email already exists")
        return False
    
    # Hash the password
    hashed_password = hash_password(password)
    
    # Get role ID from role name
    role_id = get_role_id(role)
    if role_id is None:
        # Default to User role (ID: 2) if role not found
        role_id = 2
    
    # Create the user in Supabase
    return supabase_create_user(hashed_password, email, role_id)

def authenticate_user(email: str, password: str) -> bool:
    """
    Authenticate a user with email and password.
    
    Args:
        email: Email to authenticate
        password: Password to authenticate
        
    Returns:
        True if authentication successful, False otherwise
    """
    # Special case for admin login during development
    if email.lower() == "admin" and password == "admin":
        print("Using admin development login")
        return True
    
    # Special case for existing users with plain text passwords
    if email.lower() == "gilad.rodov@gmail.com" and password.lower() == "admin":
        print("Using special case for admin user")
        return True
        
    # Get user data from Supabase using email
    print(f"Authenticating user: {email}")
    user_data = get_user(email)
    print(f"User data retrieved: {user_data}")
    
    # Check if user exists
    if not user_data:
        print("User not found in database")
        return False
    
    stored_password = user_data.get("password", "")
    
    # First check if the password is stored as plain text (for legacy accounts)
    if password == stored_password:
        print("Matched using plain text password")
        return True
    
    # If not a plain text match, try hashed comparison
    hashed_password = hash_password(password)
    print(f"Input password hash: {hashed_password[:10]}...")
    print(f"Stored password: {stored_password[:10]}...")
    
    # Compare the hashes
    result = hashed_password == stored_password
    print(f"Password match result: {result}")
    
    return result

def get_user_data(email: str) -> Optional[Dict]:
    """
    Get user data for a specific user.
    
    Args:
        email: Email to get data for
        
    Returns:
        Dictionary of user data or None if user doesn't exist
    """
    user_data = get_user(email)
    
    if user_data and 'role' in user_data:
        # Add role name to user data
        role_name = get_role_name(user_data['role'])
        if role_name:
            user_data['role_name'] = role_name
    
    return user_data

def update_user_data(email: str, data: Dict) -> bool:
    """
    Update user data for a specific user.
    
    Args:
        email: Email to update data for
        data: Dictionary of user data to update
        
    Returns:
        True if update successful, False otherwise
    """
    return update_user(email, data)

def is_admin(email: str) -> bool:
    """
    Check if a user is an admin.
    
    Args:
        email: Email to check
        
    Returns:
        True if user is an admin, False otherwise
    """
    # Special case for admin user during development
    if email.lower() == "admin":
        return True
        
    user_data = get_user_data(email)
    if not user_data or 'role' not in user_data:
        return False
    
    # Check if role is Admin (ID: 1)
    return user_data.get("role") == 1
