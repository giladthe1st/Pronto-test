"""
Debug script to check authentication issues.
"""
import streamlit as st
from utils.auth_utils import authenticate_user, get_user_data, hash_password
from database.supabase_client import get_supabase_client

def main():
    """Main debug function."""
    st.title("Authentication Debug")
    
    # Check Supabase connection
    try:
        client = get_supabase_client(use_service_role=True)
        st.success("✅ Supabase connection successful")
    except Exception as e:
        st.error(f"❌ Supabase connection failed: {e}")
        return
    
    # List all users
    try:
        response = client.table('Users').select('*').execute()
        st.subheader("Users in database:")
        
        if not response.data:
            st.warning("No users found in the database.")
        else:
            # Display users in a table
            users_table = []
            for user in response.data:
                # Don't display full password hash for security
                password_preview = user.get('password', '')[:10] + '...' if user.get('password') else 'None'
                users_table.append({
                    "ID": user.get('id'),
                    "Email": user.get('email'),
                    "Role ID": user.get('role'),
                    "Password Hash (preview)": password_preview
                })
            
            st.table(users_table)
    except Exception as e:
        st.error(f"❌ Error listing users: {e}")
    
    # Test authentication
    st.subheader("Test Authentication")
    
    col1, col2 = st.columns(2)
    
    with col1:
        email = st.text_input("Email")
    
    with col2:
        password = st.text_input("Password", type="password")
    
    if st.button("Test Login"):
        if not email or not password:
            st.error("Please enter both email and password")
        else:
            # Get user data
            user_data = get_user_data(email)
            
            if not user_data:
                st.error(f"User with email '{email}' not found in database")
            else:
                st.info(f"User found: {user_data}")
                
                # Check password hash
                hashed_input = hash_password(password)
                stored_hash = user_data.get('password', '')
                
                st.info(f"Input password hash: {hashed_input[:10]}...")
                st.info(f"Stored password hash: {stored_hash[:10]}...")
                
                if hashed_input == stored_hash:
                    st.success("✅ Password matches!")
                else:
                    st.error("❌ Password does not match")
                
                # Try authenticate_user function
                auth_result = authenticate_user(email, password)
                st.info(f"authenticate_user() result: {auth_result}")

if __name__ == "__main__":
    main()
