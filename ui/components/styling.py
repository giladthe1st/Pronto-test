"""
Styling utilities for the Pronto UI components.
"""
import streamlit as st

def apply_restaurant_styling():
    """Apply common CSS styling for restaurant display."""
    st.markdown("""
    <style>
    .restaurant-name {
        font-weight: bold;
        font-size: 1.1em;
    }
    .section-header {
        font-weight: bold;
        margin-bottom: 5px;
    }
    .vertical-spacer {
        height: 35px;
    }
    .restaurant-divider {
        border-bottom: 1px solid #f0f2f6;
        margin: 15px 0;
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)
