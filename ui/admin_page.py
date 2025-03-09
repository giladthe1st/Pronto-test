"""
Admin page component for the Pronto application.
Allows admin users to insert new rows into database tables.
"""
import streamlit as st
from database.supabase_client import get_supabase_client
from utils.auth_utils import is_admin
import pandas as pd

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
    tab1, tab2, tab3 = st.tabs(["User Management", "Restaurant Data", "Role Types"])
    
    with tab1:
        manage_users()
    
    with tab2:
        manage_restaurants()
    
    with tab3:
        manage_roles()
    
    # Return False to indicate that the main app content should not be shown
    return False

def manage_users():
    """Display user management interface."""
    st.header("User Management")
    
    # Get all users
    try:
        client = get_supabase_client(use_service_role=True)
        response = client.table('Users').select('*').execute()
        users = response.data
        
        if users:
            # Convert to DataFrame for display
            users_df = pd.DataFrame(users)
            # Hide password column for security
            if 'password' in users_df.columns:
                users_df['password'] = '********'
            
            st.dataframe(users_df)
            
            # Form to add a new user
            with st.expander("Add New User"):
                with st.form("add_user_form"):
                    email = st.text_input("Email")
                    password = st.text_input("Password", type="password")
                    
                    # Get role types for dropdown
                    role_response = client.table('RoleTypes').select('*').execute()
                    role_types = role_response.data
                    role_options = {r['role_type']: r['id'] for r in role_types}
                    
                    selected_role = st.selectbox("Role", list(role_options.keys()))
                    
                    submitted = st.form_submit_button("Add User")
                    if submitted:
                        if email and password:
                            # Hash the password (using the function from auth_utils)
                            from utils.auth_utils import hash_password
                            hashed_password = hash_password(password)
                            
                            # Create user data
                            user_data = {
                                "email": email,
                                "password": hashed_password,
                                "role": role_options[selected_role]
                            }
                            
                            # Insert the user
                            try:
                                insert_response = client.table('Users').insert(user_data).execute()
                                if insert_response.data:
                                    st.success(f"User {email} added successfully!")
                                    st.rerun()  # Refresh the page to show the new user
                                else:
                                    st.error("Failed to add user.")
                            except Exception as e:
                                st.error(f"Error adding user: {e}")
                        else:
                            st.error("Email and password are required.")
        else:
            st.info("No users found.")
    except Exception as e:
        st.error(f"Error loading users: {e}")

def manage_restaurants():
    """Display restaurant data management interface."""
    st.header("Restaurant Data")
    
    # Since restaurant data is stored in Google Sheets, we'll provide a form to add data to Supabase
    st.info("Restaurant data is currently managed in Google Sheets. This interface will allow you to create a local database for restaurants.")
    
    # Check if Restaurants table exists
    try:
        client = get_supabase_client(use_service_role=True)
        
        # Form to add a new restaurant
        with st.expander("Add New Restaurant"):
            with st.form("add_restaurant_form"):
                name = st.text_input("Restaurant Name")
                address = st.text_input("Address")
                location = st.text_input("Location/Area")
                cuisine = st.text_input("Cuisine")
                price = st.selectbox("Price Range", ["$", "$$", "$$$", "$$$$"])
                description = st.text_area("Description")
                maps_url = st.text_input("Google Maps URL")
                website = st.text_input("Website URL")
                
                submitted = st.form_submit_button("Add Restaurant")
                if submitted:
                    if name and address:
                        # Create restaurant data
                        restaurant_data = {
                            "name": name,
                            "address": address,
                            "location": location,
                            "cuisine": cuisine,
                            "price": price,
                            "description": description,
                            "maps_url": maps_url,
                            "website": website
                        }
                        
                        # Try to insert the restaurant
                        try:
                            # Check if Restaurants table exists, if not create it
                            try:
                                # This is just a check - it will fail if the table doesn't exist
                                client.table('Restaurants').select('count', count='exact').execute()
                            except Exception:
                                st.warning("Creating Restaurants table...")
                                # We would need to create the table via SQL, but that's beyond the scope here
                                # For now, just show a message
                                st.info("Please create a 'Restaurants' table in Supabase first.")
                                return
                            
                            # Insert the restaurant
                            insert_response = client.table('Restaurants').insert(restaurant_data).execute()
                            if insert_response.data:
                                st.success(f"Restaurant {name} added successfully!")
                                st.rerun()  # Refresh the page
                            else:
                                st.error("Failed to add restaurant.")
                        except Exception as e:
                            st.error(f"Error adding restaurant: {e}")
                    else:
                        st.error("Restaurant name and address are required.")
        
        # Try to display existing restaurants
        try:
            response = client.table('Restaurants').select('*').execute()
            restaurants = response.data
            
            if restaurants:
                st.subheader("Existing Restaurants")
                restaurants_df = pd.DataFrame(restaurants)
                st.dataframe(restaurants_df)
            else:
                st.info("No restaurants found in the database.")
        except Exception as e:
            st.info(f"Restaurants table may not exist yet: {e}")
            
    except Exception as e:
        st.error(f"Error accessing database: {e}")

def manage_roles():
    """Display role management interface."""
    st.header("Role Types")
    
    try:
        client = get_supabase_client(use_service_role=True)
        response = client.table('RoleTypes').select('*').execute()
        roles = response.data
        
        if roles:
            # Convert to DataFrame for display
            roles_df = pd.DataFrame(roles)
            st.dataframe(roles_df)
            
            # Form to add a new role
            with st.expander("Add New Role Type"):
                with st.form("add_role_form"):
                    role_type = st.text_input("Role Name")
                    
                    submitted = st.form_submit_button("Add Role")
                    if submitted:
                        if role_type:
                            # Create role data
                            role_data = {
                                "role_type": role_type
                            }
                            
                            # Insert the role
                            try:
                                insert_response = client.table('RoleTypes').insert(role_data).execute()
                                if insert_response.data:
                                    st.success(f"Role {role_type} added successfully!")
                                    st.rerun()  # Refresh the page to show the new role
                                else:
                                    st.error("Failed to add role.")
                            except Exception as e:
                                st.error(f"Error adding role: {e}")
                        else:
                            st.error("Role name is required.")
        else:
            st.info("No roles found.")
    except Exception as e:
        st.error(f"Error loading roles: {e}")
