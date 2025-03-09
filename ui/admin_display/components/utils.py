"""
Utility functions for admin components.
"""
import streamlit as st
import pandas as pd
from database.supabase_client import get_supabase_client

def display_data_table(data, title=None):
    """
    Display data in a Streamlit dataframe with an optional title.
    
    Args:
        data (list): List of dictionaries containing the data
        title (str, optional): Title to display above the dataframe
    """
    if title:
        st.subheader(title)
        
    if data:
        df = pd.DataFrame(data)
        st.dataframe(df)
    else:
        st.info(f"No {title.lower() if title else 'data'} found in the database.")

def get_table_data(table_name, use_service_role=True):
    """
    Get all data from a specified table.
    
    Args:
        table_name (str): Name of the table to query
        use_service_role (bool): Whether to use service role for the query
        
    Returns:
        list: Data from the table or empty list if error
    """
    try:
        client = get_supabase_client(use_service_role=use_service_role)
        response = client.table(table_name).select('*').execute()
        return response.data
    except Exception as e:
        st.info(f"{table_name} table may not exist yet: {e}")
        return []

def get_dropdown_options(table_name, id_field='id', name_field='name', use_service_role=True):
    """
    Get options for a dropdown from a table.
    
    Args:
        table_name (str): Name of the table to query
        id_field (str): Field to use as the value
        name_field (str): Field to use as the display name
        use_service_role (bool): Whether to use service role for the query
        
    Returns:
        dict: Dictionary mapping display names to values
    """
    try:
        client = get_supabase_client(use_service_role=use_service_role)
        response = client.table(table_name).select(f'{id_field}, {name_field}').execute()
        data = response.data
        return {item[name_field]: item[id_field] for item in data}
    except Exception:
        return {}

def insert_record(table_name, data, use_service_role=True):
    """
    Insert a record into a table.
    
    Args:
        table_name (str): Name of the table to insert into
        data (dict): Data to insert
        use_service_role (bool): Whether to use service role for the operation
        
    Returns:
        tuple: (success, message) where success is a boolean and message is a string
    """
    try:
        client = get_supabase_client(use_service_role=use_service_role)
        response = client.table(table_name).insert(data).execute()
        if response.data:
            return True, f"Record added successfully!"
        else:
            return False, "Failed to add record."
    except Exception as e:
        error_msg = str(e)
        if "duplicate key value" in error_msg:
            return False, "This record already exists."
        return False, f"Error adding record: {e}"
