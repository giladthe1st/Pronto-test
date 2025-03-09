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
    
    key = SUPABASE_SERVICE_KEY if use_service_role else SUPABASE_KEY
    
    if not key:
        key_type = "service key" if use_service_role else "API key"
        raise ValueError(f"Supabase {key_type} not found in configuration")
    
    # Handle different versions of the Supabase client
    # Some versions accept 'proxy' parameter, others don't
    try:
        # First try without any extra parameters
        return create_client(SUPABASE_URL, key)
    except TypeError as e:
        # If we get a TypeError about missing 'proxy', try with proxy=None
        if "proxy" in str(e):
            st.warning("Using compatibility mode for Supabase client")
            # For older versions that require the proxy parameter
            return create_client(SUPABASE_URL, key, options={"proxy": None})
        # If it's some other error, re-raise it
        raise

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
        response = client.table('Users').select('email').eq('email', email).execute()
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
        
        response = client.table('Users').insert(user_data).execute()
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
        response = client.table('Users').select('*').eq('email', email).execute()
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
        
        response = client.table('Users').update(data).eq('email', email).execute()
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
        response = client.table('RoleTypes').select('*').execute()
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
        response = client.table('RoleTypes').select('role_type').eq('id', role_id).execute()
        
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
        response = client.table('RoleTypes').select('id').eq('role_type', role_name).execute()
        
        if len(response.data) > 0:
            return response.data[0]['id']
        return None
    except Exception as e:
        st.error(f"Error getting role ID: {e}")
        return None

# Restaurant data functions
def get_restaurants(filters=None, use_service_role=True) -> List[Dict]:
    """
    Get restaurant data from the database with optional filtering.
    
    Args:
        filters (dict, optional): Dictionary of filter conditions
        use_service_role (bool): Whether to use service role for the query
        
    Returns:
        List of restaurant dictionaries
    """
    try:
        client = get_supabase_client(use_service_role=use_service_role)
        
        # Start with a base query
        query = client.table('Restaurants').select('*')
        
        # Apply filters if provided
        if filters:
            for field, value in filters.items():
                if isinstance(value, list):
                    # For list values, use 'in' operator
                    query = query.in_(field, value)
                else:
                    # For single values, use 'eq' operator
                    query = query.eq(field, value)
        
        # Execute the query
        response = query.execute()
        restaurants = response.data
        
        print(f"Found {len(restaurants)} restaurants")
        
        # If we have restaurants, fetch deals for each one
        if restaurants:
            # Get all deals
            deals_response = client.table('Deals').select('*').execute()
            deals = deals_response.data
            
            print(f"Found {len(deals)} deals in the Deals table")
            
            # Create a mapping of restaurant_id to deals
            restaurant_deals = {}
            for deal in deals:
                restaurant_id = deal.get('restaurant_id')
                if restaurant_id not in restaurant_deals:
                    restaurant_deals[restaurant_id] = []
                restaurant_deals[restaurant_id].append(deal)
            
            # Add deals to each restaurant
            for restaurant in restaurants:
                restaurant_id = restaurant.get('id')
                print(f"Processing restaurant ID: {restaurant_id}, Name: {restaurant.get('name', 'Unknown')}")
                
                # Print available fields in restaurant
                print(f"Restaurant fields: {list(restaurant.keys())}")
                
                if restaurant_id in restaurant_deals:
                    # Get deals for this restaurant
                    restaurant_deals_list = restaurant_deals[restaurant_id]
                    print(f"  Found {len(restaurant_deals_list)} deals for restaurant {restaurant_id}")
                    
                    # Format deals for the UI
                    if restaurant_deals_list:
                        # Create summarized_deals and detailed_deals strings
                        summarized_deals = []
                        detailed_deals = []
                        
                        for deal in restaurant_deals_list:
                            summarized_deals.append(deal.get('summarized_deal', ''))
                            detailed_deals.append(deal.get('details', ''))
                        
                        # Join with the separator expected by the UI
                        restaurant['summarized_deals'] = ' -> '.join(summarized_deals)
                        restaurant['detailed_deals'] = ' -> '.join(detailed_deals)
                        
                        # Legacy format for backward compatibility
                        restaurant['deals'] = restaurant['summarized_deals']
                        
                        print(f"  Added deals to restaurant {restaurant_id}: {restaurant['deals']}")
                else:
                    print(f"  No deals found for restaurant {restaurant_id}")
        
        return restaurants
    except Exception as e:
        print(f"Error getting restaurants: {e}")
        return []

def get_restaurant_categories(restaurant_id=None, use_service_role=True) -> List[Dict]:
    """
    Get restaurant categories with optional filtering by restaurant ID.
    
    Args:
        restaurant_id (int, optional): Filter by specific restaurant ID
        use_service_role (bool): Whether to use service role for the query
        
    Returns:
        List of restaurant category dictionaries
    """
    try:
        client = get_supabase_client(use_service_role=use_service_role)
        query = client.table('Restaurant_Categories').select('*')
        
        if restaurant_id:
            query = query.eq('restaurant_id', restaurant_id)
            
        response = query.execute()
        return response.data
    except Exception as e:
        st.error(f"Error retrieving restaurant categories: {e}")
        return []

def get_restaurant_with_details(restaurant_id, use_service_role=True) -> Optional[Dict]:
    """
    Get a restaurant with all its related details (categories, menu items, etc.)
    
    Args:
        restaurant_id: ID of the restaurant to retrieve
        use_service_role (bool): Whether to use service role for the query
        
    Returns:
        Dictionary with restaurant data and related details or None if not found
    """
    try:
        client = get_supabase_client(use_service_role=use_service_role)
        
        # Get the restaurant
        restaurant_response = client.table('Restaurants').select('*').eq('id', restaurant_id).execute()
        
        if not restaurant_response.data:
            return None
            
        restaurant = restaurant_response.data[0]
        
        # Get categories for this restaurant
        categories_response = client.table('Restaurant_Categories')\
            .select('category_id')\
            .eq('restaurant_id', restaurant_id)\
            .execute()
            
        category_ids = [item['category_id'] for item in categories_response.data]
        
        if category_ids:
            categories_response = client.table('Categories')\
                .select('*')\
                .in_('id', category_ids)\
                .execute()
            restaurant['categories'] = categories_response.data
        else:
            restaurant['categories'] = []
        
        # Add any other related data here (deals, menu items, etc.)
        
        return restaurant
    except Exception as e:
        st.error(f"Error retrieving restaurant with details: {e}")
        return None

def process_restaurant_data_from_db(restaurants):
    """
    Process restaurant data from the database to match the format expected by the UI.
    
    Args:
        restaurants: List of restaurant dictionaries from the database
        
    Returns:
        List of processed restaurant dictionaries
    """
    if not restaurants:
        return []
        
    processed_restaurants = []
    
    for restaurant in restaurants:
        processed = restaurant.copy()
        
        print(f"Processing restaurant for UI: {processed.get('name', 'Unknown')}")
        print(f"Original fields: {list(processed.keys())}")
        
        # Map database field names to UI expected field names
        field_mappings = {
            'average_rating': 'rating',
            'reviews_count': 'review_count',
            'website_url': 'website',
            'logo_url': 'logo_url',
            'maps_url': 'maps_url'
        }
        
        for db_field, ui_field in field_mappings.items():
            if db_field in processed:
                processed[ui_field] = processed.get(db_field)
                print(f"Mapped {db_field} -> {ui_field}: {processed[ui_field]}")
        
        # Set default values for missing fields
        if 'rating' not in processed or processed['rating'] is None:
            processed['rating'] = 0.0
            
        if 'review_count' not in processed or processed['review_count'] is None:
            processed['review_count'] = 0
            
        if 'distance' not in processed:
            processed['distance'] = 'Unknown'
            
        # Ensure website field exists
        if 'website' not in processed or processed['website'] is None:
            processed['website'] = '#'
            
        # Ensure location field exists (using address)
        if 'location' not in processed:
            processed['location'] = processed.get('address', '')
            
        # Ensure other required fields exist
        for field in ['address', 'logo_url', 'maps_url', 'menu_url']:
            if field not in processed or processed[field] is None:
                processed[field] = ''
        
        # Since reviews_data isn't directly in the schema, we'll create it from available data
        rating = processed.get('rating', 0)
        review_count = processed.get('review_count', 0)
        
        # Check if we have any reviews
        if review_count > 0:
            processed['reviews_data'] = f"Rating: {rating}/10"
            processed['reviews'] = processed['reviews_data']
            print(f"Created reviews data: {processed['reviews_data']}")
        else:
            processed['reviews_data'] = ''
            processed['reviews'] = ''
            print("No reviews available")
        
        # Deals will be handled by the get_restaurants function
        # Just ensure the fields exist with defaults
        for field in ['deals', 'summarized_deals', 'detailed_deals']:
            if field not in processed or processed[field] is None:
                processed[field] = ''
            
        # Ensure coordinates exist
        if ('latitude' not in processed or processed['latitude'] is None or
            'longitude' not in processed or processed['longitude'] is None):
            # Default to downtown Winnipeg if no coordinates
            processed['latitude'] = 49.8951
            processed['longitude'] = -97.1384
        
        print(f"Final UI fields: {list(processed.keys())}")
        processed_restaurants.append(processed)
    
    return processed_restaurants
