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
            return ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
        
        # Next, try to use Streamlit secrets
        elif hasattr(st, 'secrets') and 'GOOGLE_CREDENTIALS' in st.secrets:
            try:
                # Get credentials from Streamlit secrets
                credentials_str = st.secrets['GOOGLE_CREDENTIALS']
                
                # If credentials_str is already a dictionary (Streamlit might parse it automatically)
                if isinstance(credentials_str, dict):
                    credentials_json = credentials_str
                else:
                    # Otherwise, parse the string
                    # Remove any triple quotes that might be included in the secret
                    if credentials_str.startswith('"""') and credentials_str.endswith('"""'):
                        credentials_str = credentials_str[3:-3]
                    
                    # Strip any leading/trailing whitespace
                    credentials_str = credentials_str.strip()
                    
                    # Parse the JSON string
                    credentials_json = json.loads(credentials_str)
                
                return ServiceAccountCredentials.from_json_keyfile_dict(credentials_json, scope)
            except json.JSONDecodeError as json_err:
                st.error(f"Error parsing Google credentials JSON from Streamlit secrets: {json_err}")
                st.info("Please ensure your JSON credentials in Streamlit secrets are properly formatted.")
                return None
        
        # If no Streamlit secrets, try environment variables
        elif 'GOOGLE_CREDENTIALS' in os.environ:
            try:
                # Get credentials from environment variable
                credentials_str = os.environ['GOOGLE_CREDENTIALS']
                # Replace any literal \n with actual newlines to ensure proper JSON parsing
                credentials_str = credentials_str.replace('\\n', '\n')
                credentials_json = json.loads(credentials_str)
                return ServiceAccountCredentials.from_json_keyfile_dict(credentials_json, scope)
            except json.JSONDecodeError as json_err:
                st.error(f"Error parsing Google credentials JSON from environment: {json_err}")
                st.info("Please ensure your JSON credentials are properly formatted without invalid control characters.")
                return None
        
        else:
            st.warning("No Google credentials found. Please provide a service account JSON file or set GOOGLE_CREDENTIALS in Streamlit secrets or environment variables.")
            return None
            
    except Exception as e:
        st.error(f"Error getting Google credentials: {e}")
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
            return gspread.authorize(credentials)
        except Exception as e:
            st.error(f"Error authorizing Google Sheets client: {e}")
    
    return None
