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
        
        # If no file path or file doesn't exist, try environment variables
        elif 'GOOGLE_CREDENTIALS' in os.environ:
            # Get credentials from environment variable
            credentials_json = json.loads(os.environ['GOOGLE_CREDENTIALS'])
            return ServiceAccountCredentials.from_json_keyfile_dict(credentials_json, scope)
        
        else:
            st.warning("No Google credentials found. Please provide a service account JSON file or set GOOGLE_CREDENTIALS environment variable.")
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
