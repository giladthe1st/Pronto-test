import pandas as pd
import streamlit as st
from typing import Optional, Dict, Any, List
import traceback
from google_auth import get_sheet_client

class DataHandler:
    """Class to handle loading and processing restaurant data."""
    
    @staticmethod
    def load_from_csv(file_path: str) -> pd.DataFrame:
        """Load restaurant data from a CSV file."""
        try:
            df = pd.read_csv(file_path)
            return df
        except Exception as e:
            st.error(f"Error loading data from CSV: {e}")
            return pd.DataFrame()
    
    @staticmethod
    def load_from_google_sheets(sheet_id: str, sheet_name: Optional[str] = None, credentials_path: Optional[str] = None) -> pd.DataFrame:
        """
        Load restaurant data from a Google Sheet.
        
        Args:
            sheet_id (str): The ID of the Google Sheet (from the URL).
            sheet_name (str, optional): The name of the specific worksheet to load.
                If None, the first worksheet will be used.
            credentials_path (str, optional): Path to the Google API credentials JSON file.
                If None, will try to use environment variables.
                
        Returns:
            pd.DataFrame: DataFrame containing the sheet data or empty DataFrame if loading fails.
        """
        try:
            # Get the Google Sheets client
            client = get_sheet_client(credentials_path)
            
            if not client:
                st.error("Failed to authenticate with Google Sheets API.")
                print("Failed to authenticate with Google Sheets API. Check your credentials.")
                return pd.DataFrame()
            
            try:
                # Open the spreadsheet
                print(f"Attempting to open spreadsheet with ID: {sheet_id}")
                spreadsheet = client.open_by_key(sheet_id)
                
                # Get the specific worksheet or default to first
                if sheet_name:
                    print(f"Attempting to access worksheet: {sheet_name}")
                    worksheet = spreadsheet.worksheet(sheet_name)
                else:
                    print("Accessing first worksheet")
                    worksheet = spreadsheet.get_worksheet(0)
                
                # Get all values including the header row
                print("Retrieving data from worksheet")
                data = worksheet.get_all_values()
                
                if not data:
                    st.warning("No data found in the specified Google Sheet.")
                    print("No data found in the specified Google Sheet.")
                    return pd.DataFrame()
                
                # Convert to DataFrame (first row as header)
                headers = data[0]
                rows = data[1:]
                
                # Create DataFrame
                df = pd.DataFrame(rows, columns=headers)
                
                # Convert numeric columns to appropriate types
                for col in df.columns:
                    # Try to convert to numeric, but ignore errors
                    df[col] = pd.to_numeric(df[col], errors='ignore')
                
                print(f"Successfully retrieved data with {len(df)} rows and {len(df.columns)} columns")
                return df
            
            except Exception as e:
                st.error(f"Error accessing Google Sheet: {e}")
                print(f"Error accessing Google Sheet: {e}")
                print("This could be due to permission issues. Make sure you've shared the spreadsheet with the service account email.")
                print("Service account email can be found in your credentials.json file.")
                traceback.print_exc()
                return pd.DataFrame()
                
        except Exception as e:
            st.error(f"Error loading data from Google Sheets: {e}")
            print(f"Error loading data from Google Sheets: {e}")
            traceback.print_exc()
            return pd.DataFrame()
    
    @staticmethod
    def format_restaurant_data(df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Convert DataFrame to a list of restaurant dictionaries for easy display."""
        if df.empty:
            return []
        
        return df.to_dict(orient='records')
