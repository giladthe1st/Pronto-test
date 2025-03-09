"""
Utility functions for application startup in the Pronto application.
"""
import os
import glob
import streamlit as st
from utils.image_handler import CACHE_DIR

def clear_data_on_startup():
    """
    Clear cached images to ensure fresh data is downloaded.
    This function is designed to run only once when the server starts,
    not on every browser refresh.
    """
    # Use Streamlit's session state to track if this is the first run
    if 'server_has_started' not in st.session_state:
        print("Server starting for the first time - clearing cache for fresh download...")
        
        # Clear logo images directory
        logo_dir = "logo_images"
        if os.path.exists(logo_dir) and os.path.isdir(logo_dir):
            try:
                # Remove all files in the directory
                for file_path in glob.glob(f"{logo_dir}/*"):
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                print(f"Cleared all files in {logo_dir}")
            except Exception as e:
                print(f"Error clearing {logo_dir}: {e}")
        
        # Clear cached images directory
        if os.path.exists(CACHE_DIR) and os.path.isdir(CACHE_DIR):
            try:
                # Remove all files in the directory
                for file_path in glob.glob(f"{CACHE_DIR}/*"):
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                print(f"Cleared all files in {CACHE_DIR}")
            except Exception as e:
                print(f"Error clearing {CACHE_DIR}: {e}")
        
        # Mark that the server has started
        st.session_state.server_has_started = True
        print("Cache clearing complete. Server is ready.")
    else:
        # This is just a page refresh, not a server restart
        pass
