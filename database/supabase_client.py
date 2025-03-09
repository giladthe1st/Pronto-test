"""
Supabase client for the Pronto application.
Handles database connections and operations.
"""
import os
from typing import Dict, List, Optional
from supabase import create_client, Client
import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env file (for local development)
load_dotenv()

# Function to get configuration from either Streamlit secrets or environment variables
def get_config_value(key: str) -> Optional[str]:
    """
    Get configuration value from either Streamlit secrets or environment variables.
    Streamlit secrets take precedence for deployed environments.
    
    Args:
        key: The configuration key to look for
        
    Returns:
        The configuration value or None if not found
    """
    # First try to get from Streamlit secrets (for deployed app)
    if 'supabase' in st.secrets and key in st.secrets['supabase']:
        return st.secrets['supabase'][key]
    
    # Then try to get from environment variables (for local development)
    return os.environ.get(key)

# Load Supabase credentials
SUPABASE_URL = get_config_value("supabase_project_url")
SUPABASE_KEY = get_config_value("supabase_api_key")
SUPABASE_SERVICE_KEY = get_config_value("supabase_service_key")

def get_supabase_client(use_service_role=False) -> Client:
    """
    Get a Supabase client instance.
    
    Args:
        use_service_role: Whether to use the service role key for admin operations
    
    Returns:
        Supabase client instance
    """
    if not SUPABASE_URL:
        raise ValueError("Supabase URL not found in configuration")
    
    if use_service_role:
        if not SUPABASE_SERVICE_KEY:
            raise ValueError("Supabase service key not found in configuration")
        return create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    else:
        if not SUPABASE_KEY:
            raise ValueError("Supabase API key not found in configuration")
        return create_client(SUPABASE_URL, SUPABASE_KEY)

# User management functions
def user_exists(email: str) -> bool:
    """
    Check if a user exists in the database.
    
    Args:
        email: Email to check
        
    Returns:
        True if user exists, False otherwise
    """
    try:
        client = get_supabase_client()
        response = client.table('User').select('email').eq('email', email).execute()
        return len(response.data) > 0
    except Exception as e:
        st.error(f"Error checking if user exists: {e}")
        return False

def create_user(password: str, email: str, role_id: int = 2) -> bool:
    """
    Create a new user in the database.
    
    Args:
        password: Password for the new user
        email: Email for the new user
        role_id: Role ID for the new user (default: 2 for regular user)
        
    Returns:
        True if creation successful, False otherwise
    """
    try:
        # Use service role key for user creation to bypass RLS policies
        client = get_supabase_client(use_service_role=True)
        
        # Create user record
        user_data = {
            "password": password,
            "email": email,
            "role": role_id
        }
        
        response = client.table('User').insert(user_data).execute()
        return len(response.data) > 0
    except Exception as e:
        st.error(f"Error creating user: {e}")
        return False

def get_user(email: str) -> Optional[Dict]:
    """
    Get user data for a specific user.
    
    Args:
        email: Email to get data for
        
    Returns:
        Dictionary of user data or None if user doesn't exist
    """
    try:
        # Get client with service role to bypass RLS policies
        client = get_supabase_client(use_service_role=True)
        
        # Now try to get the specific user
        response = client.table('User').select('*').eq('email', email).execute()
        if hasattr(response, 'data') and len(response.data) > 0:
            return response.data[0]
        return None
    except Exception as e:
        st.error(f"Error getting user data: {e}")
        return None

def update_user(email: str, data: Dict) -> bool:
    """
    Update user data for a specific user.
    
    Args:
        email: Email to update data for
        data: Dictionary of user data to update
        
    Returns:
        True if update successful, False otherwise
    """
    try:
        # Use service role key for user update to bypass RLS policies
        client = get_supabase_client(use_service_role=True)
        
        response = client.table('User').update(data).eq('email', email).execute()
        return len(response.data) > 0
    except Exception as e:
        st.error(f"Error updating user data: {e}")
        return False

def get_role_types() -> List[Dict]:
    """
    Get all role types from the database.
    
    Returns:
        List of role types
    """
    try:
        client = get_supabase_client()
        response = client.table('RoleType').select('*').execute()
        return response.data
    except Exception as e:
        st.error(f"Error getting role types: {e}")
        return []

def get_role_name(role_id: int) -> Optional[str]:
    """
    Get the name of a role by its ID.
    
    Args:
        role_id: ID of the role
        
    Returns:
        Role name or None if not found
    """
    try:
        client = get_supabase_client()
        response = client.table('RoleType').select('role_type').eq('id', role_id).execute()
        
        if len(response.data) > 0:
            return response.data[0]['role_type']
        return None
    except Exception as e:
        st.error(f"Error getting role name: {e}")
        return None

def get_role_id(role_name: str) -> Optional[int]:
    """
    Get the ID of a role by its name.
    
    Args:
        role_name: Name of the role
        
    Returns:
        Role ID or None if not found
    """
    try:
        client = get_supabase_client()
        response = client.table('RoleType').select('id').eq('role_type', role_name).execute()
        
        if len(response.data) > 0:
            return response.data[0]['id']
        return None
    except Exception as e:
        st.error(f"Error getting role ID: {e}")
        return None

# Favorites management functions
def get_favorites(user_id: int) -> List[str]:
    """
    Get a user's favorite restaurants.
    
    Args:
        user_id: User ID to get favorites for
        
    Returns:
        List of restaurant IDs in favorites
    """
    try:
        client = get_supabase_client()
        response = client.table('Favorites').select('restaurant_id').eq('user_id', user_id).execute()
        
        if len(response.data) > 0:
            return [item['restaurant_id'] for item in response.data]
        return []
    except Exception as e:
        st.error(f"Error getting favorites: {e}")
        return []

def add_favorite(user_id: int, restaurant_id: str) -> bool:
    """
    Add a restaurant to a user's favorites.
    
    Args:
        user_id: User ID to update
        restaurant_id: ID of restaurant to add to favorites
        
    Returns:
        True if update successful, False otherwise
    """
    try:
        client = get_supabase_client()
        
        # Check if favorite already exists
        response = client.table('Favorites').select('*').eq('user_id', user_id).eq('restaurant_id', restaurant_id).execute()
        
        if len(response.data) > 0:
            # Already a favorite
            return True
        
        # Add to favorites
        favorite_data = {
            "user_id": user_id,
            "restaurant_id": restaurant_id
        }
        
        response = client.table('Favorites').insert(favorite_data).execute()
        return len(response.data) > 0
    except Exception as e:
        st.error(f"Error adding favorite: {e}")
        return False
