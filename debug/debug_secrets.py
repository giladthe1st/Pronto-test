"""
Debug utility to check Streamlit secrets configuration.
This is a temporary file to help diagnose authentication issues.
"""
import streamlit as st
import json
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
    
    # Check for individual credential keys directly in st.secrets
    st.write("## Individual Credential Keys Check")
    required_keys = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email', 
                    'client_id', 'auth_uri', 'token_uri', 'auth_provider_x509_cert_url', 
                    'client_x509_cert_url', 'universe_domain']
    
    found_keys = []
    missing_keys = []
    
    for key in required_keys:
        if hasattr(st.secrets, key):
            found_keys.append(key)
        else:
            missing_keys.append(key)
    
    if found_keys:
        st.write(f"Found these credential keys directly in st.secrets: {found_keys}")
        
        # Check private key format if it exists
        if 'private_key' in found_keys:
            pk = st.secrets.private_key
            pk_start = pk[:15] + "..." if pk else "Empty"
            st.write(f"Private key starts with: {pk_start}")
            st.write(f"Private key length: {len(pk) if pk else 0}")
            
            # Check if it's properly formatted
            if pk and "-----BEGIN PRIVATE KEY-----" in pk:
                st.success("Private key appears to be properly formatted")
            else:
                st.error("Private key format issue detected")
    
    if missing_keys:
        st.error(f"Missing these credential keys: {missing_keys}")
    
    # Check specifically for gcp_service_account
    has_gcp = "gcp_service_account" in st.secrets
    st.write(f"Has gcp_service_account section: {has_gcp}")
    
    if has_gcp:
        # Check for required keys (without revealing values)
        gcp_keys = list(st.secrets.gcp_service_account.keys())
        st.write(f"Keys in gcp_service_account: {gcp_keys}")
        
        # Check for required keys
        required_keys = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email']
        missing_keys = [key for key in required_keys if key not in gcp_keys]
        
        if missing_keys:
            st.error(f"Missing required keys in gcp_service_account: {missing_keys}")
        else:
            st.success("All required keys present in gcp_service_account")
            
            # Check private key format (just show first few chars)
            if "private_key" in gcp_keys:
                pk = st.secrets.gcp_service_account.private_key
                pk_start = pk[:15] + "..." if pk else "Empty"
                st.write(f"Private key starts with: {pk_start}")
                st.write(f"Private key length: {len(pk) if pk else 0}")
                
                # Check if it's properly formatted
                if pk and "-----BEGIN PRIVATE KEY-----" in pk:
                    st.success("Private key appears to be properly formatted")
                else:
                    st.error("Private key format issue detected")

# Check environment variables
st.write("## Environment Variables Check")
has_env_creds = "GOOGLE_CREDENTIALS" in os.environ
st.write(f"Has GOOGLE_CREDENTIALS environment variable: {has_env_creds}")

if has_env_creds:
    # Try to parse the JSON
    try:
        creds_json = json.loads(os.environ["GOOGLE_CREDENTIALS"])
        st.write(f"GOOGLE_CREDENTIALS contains valid JSON with keys: {list(creds_json.keys())}")
    except json.JSONDecodeError as e:
        st.error(f"GOOGLE_CREDENTIALS contains invalid JSON: {e}")

# Check for credentials file
st.write("## Credentials File Check")
creds_file = "credentials.json"
has_file = os.path.exists(creds_file)
st.write(f"Has credentials.json file: {has_file}")

st.write("## Debugging Complete")
st.write("Please check the logs for additional information.")
