"""
Categories management component for admin interface.
"""
import streamlit as st
import pandas as pd
from database.supabase_client import get_supabase_client

def manage_categories():
    """Display categories management interface."""
    st.header("Categories")
    
    try:
        client = get_supabase_client(use_service_role=True)
        
        # Display information about the Category enumerated type
        st.info("Categories in Supabase are managed as an enumerated type with predefined values (Italian, Indian, Sushi).")
        
        # Show the current enumerated values
        st.subheader("Current Category Values")
        category_values = ["Italian", "Indian", "Sushi"]  # Hardcoded based on the screenshot
        categories_df = pd.DataFrame({"category_type": category_values})
        st.dataframe(categories_df)
        
        # Note: Adding new enumerated values would require SQL ALTER TYPE commands
        # which are beyond the scope of this simple admin interface
        st.warning("Adding new category types requires database schema changes. Please use the Supabase dashboard to modify the Category enumerated type.")
            
    except Exception as e:
        st.error(f"Error accessing database: {e}")
