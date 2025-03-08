"""
Utility functions for loading and processing restaurant data.
"""
import os
import pandas as pd
import streamlit as st
from data_handler import DataHandler

@st.cache_data(ttl=3600, show_spinner=False)  # Cache for 1 hour, hide default spinner
def download_google_sheet_data():
    """Download data from Google Sheets and save locally for faster access."""
    # Define file paths
    data_dir = "data"
    local_file = os.path.join(data_dir, "restaurant_data.csv")
    
    # Check if local file exists and use it as fallback
    local_data_exists = os.path.exists(local_file)
    
    # Ensure data directory exists
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    # Use the specific Google Sheet ID for the restaurant data
    # From: https://docs.google.com/spreadsheets/d/14IK_ep3q3oPgVQP6oRPttgESuT4FhLiED01mCZW3SSI/edit?gid=623368112
    sheet_id = "14IK_ep3q3oPgVQP6oRPttgESuT4FhLiED01mCZW3SSI"
    sheet_name = "refined_data"  # Specific sheet name to use
    
    # Try to get credentials path from environment variable first
    credentials_path = os.environ.get("GOOGLE_CREDENTIALS_PATH", "credentials.json")
    
    # Create a placeholder for status messages
    status_message = st.empty()
    
    try:
        # This message will only show when actually downloading, not when using cache
        print("Downloading data from Google Sheets...")
        
        # Use DataHandler to load from Google Sheets with specific sheet name
        df = DataHandler.load_from_google_sheets(sheet_id, sheet_name=sheet_name, credentials_path=credentials_path)
        
        if not df.empty:
            # Save to local file for future use
            df.to_csv(local_file, index=False)
            print("Data successfully downloaded and saved locally")
            return df
        else:
            raise Exception("Received empty dataframe from Google Sheets")
    except Exception as e:
        error_msg = f"Error downloading data from Google Sheets: {e}"
        with status_message.container():
            st.error(error_msg)
        
        # In production, log the error to a monitoring system
        print(f"PRODUCTION ERROR: {error_msg}")
        
        # If we have local data, use it as fallback
        if local_data_exists:
            with status_message.container():
                st.warning("Using locally cached data as fallback")
            return pd.read_csv(local_file)
        
        # If all else fails, return empty DataFrame
        return pd.DataFrame()
