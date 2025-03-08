"""
Google Authentication Helper for accessing Google Sheets.
This module provides functions to authenticate with Google API.
"""
import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st

def get_google_credentials(credentials_path=None):
    """
    Get Google API credentials either from a service account JSON file or from environment variables.
    
    Args:
        credentials_path (str, optional): Path to the service account JSON file.
            If None, will try to use environment variables.
    
    Returns:
        ServiceAccountCredentials: The credentials object for Google API.
    """
    # Define the scope
    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]
    
    try:
        # First try to use credentials file if provided
        if credentials_path and os.path.exists(credentials_path):
            print(f"Using credentials file: {credentials_path}")
            return ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
        
        # Check for Streamlit secrets (for deployed environment)
        elif hasattr(st, 'secrets'):
            print("Checking Streamlit secrets...")
            
            # Debug: Print available secret keys
            if hasattr(st.secrets, '_secrets'):
                print(f"Available secret sections: {list(st.secrets._secrets.keys())}")
            
            if 'gcp_service_account' in st.secrets:
                print("Found gcp_service_account in Streamlit secrets")
                
                # Get credentials from Streamlit secrets
                credentials_dict = dict(st.secrets["gcp_service_account"])
                
                # Debug: Print keys in credentials dict (without sensitive values)
                print(f"Keys in credentials dict: {list(credentials_dict.keys())}")
                
                if 'type' in credentials_dict and 'private_key' in credentials_dict:
                    print("Required fields found in credentials dict")
                    return ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
                else:
                    missing_keys = []
                    for key in ['type', 'project_id', 'private_key_id', 'private_key', 'client_email']:
                        if key not in credentials_dict:
                            missing_keys.append(key)
                    
                    print(f"Missing required keys in credentials dict: {missing_keys}")
                    st.error(f"Missing required keys in Google credentials: {', '.join(missing_keys)}")
                    return None
            else:
                print("No gcp_service_account found in Streamlit secrets")
        
        # If no file path or file doesn't exist, try environment variables
        elif 'GOOGLE_CREDENTIALS' in os.environ:
            print("Using GOOGLE_CREDENTIALS environment variable")
            try:
                # Get credentials from environment variable
                credentials_json = json.loads(os.environ['GOOGLE_CREDENTIALS'])
                return ServiceAccountCredentials.from_json_keyfile_dict(credentials_json, scope)
            except json.JSONDecodeError as e:
                st.error(f"Error parsing GOOGLE_CREDENTIALS: {e}")
                print(f"Error parsing GOOGLE_CREDENTIALS: {e}")
                print("This could be due to improper formatting of the JSON string.")
                return None
        
        else:
            print("No credentials found in file, Streamlit secrets, or environment variables")
            st.warning("No Google credentials found. Please provide a service account JSON file or set GOOGLE_CREDENTIALS environment variable.")
            return None
            
    except Exception as e:
        st.error(f"Error getting Google credentials: {e}")
        print(f"Error getting Google credentials: {e}")
        print(f"Exception details: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def get_sheet_client(credentials_path=None):
    """
    Get an authorized Google Sheets client.
    
    Args:
        credentials_path (str, optional): Path to the service account JSON file.
    
    Returns:
        gspread.Client: Authorized Google Sheets client or None if authentication fails.
    """
    credentials = get_google_credentials(credentials_path)
    
    if credentials:
        try:
            print("Successfully obtained credentials, authorizing gspread client")
            return gspread.authorize(credentials)
        except Exception as e:
            st.error(f"Error authorizing Google Sheets client: {e}")
            print(f"Error authorizing Google Sheets client: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("Failed to get credentials, cannot authorize gspread client")
    
    return None
