"""
Debug utility to check Streamlit secrets configuration.
This is a temporary file to help diagnose authentication issues.
"""
import streamlit as st
import os

st.title("Streamlit Secrets Debugger")

# Check if running in Streamlit Cloud
st.write("## Environment Check")
is_cloud = os.environ.get("STREAMLIT_SHARING") == "true"
st.write(f"Running in Streamlit Cloud: {is_cloud}")

# Check for secrets
st.write("## Secrets Check")
has_secrets = hasattr(st, "secrets")
st.write(f"Has st.secrets: {has_secrets}")

if has_secrets:
    # Check for secret sections (without revealing actual values)
    if hasattr(st.secrets, "_secrets"):
        secret_sections = list(st.secrets._secrets.keys())
        st.write(f"Secret sections: {secret_sections}")
    else:
        st.write("No _secrets attribute found")
    
    # Check for Supabase credentials
    st.write("## Supabase Credentials Check")
    has_supabase = "supabase_url" in st.secrets and "supabase_key" in st.secrets
    st.write(f"Has Supabase credentials: {has_supabase}")
    
    if has_supabase:
        # Show partial URL (safe to show)
        supabase_url = st.secrets.supabase_url
        if supabase_url:
            url_parts = supabase_url.split(".")
            if len(url_parts) > 1:
                masked_url = f"{url_parts[0][:4]}...{url_parts[-1]}"
                st.write(f"Supabase URL format: {masked_url}")
        
        # Check key format (don't show actual key)
        supabase_key = st.secrets.supabase_key
        if supabase_key:
            key_length = len(supabase_key)
            st.write(f"Supabase key length: {key_length}")
            if key_length > 30:
                st.success("Supabase key appears to be valid")
            else:
                st.warning("Supabase key seems too short")

# Check for credentials file
st.write("## Credentials File Check")
creds_file = "credentials.json"
has_file = os.path.exists(creds_file)
st.write(f"Has credentials.json file: {has_file}")

st.write("## Debugging Complete")
st.write("Please check the logs for additional information.")
