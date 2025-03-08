"""
Deal display functionality for restaurant UI.
"""
import os
import streamlit as st

def check_flyer_existence(restaurant_name):
    """
    Check if a flyer exists for a restaurant.
    
    Args:
        restaurant_name: Name of the restaurant
        
    Returns:
        tuple: (bool indicating if flyer exists, path to flyer)
    """
    flyer_path = f"flyers/{restaurant_name.lower().replace(' ', '_')}_flyer.jpg"
    return os.path.exists(flyer_path), flyer_path

def display_deal_section(restaurant, flyer_existence, text_filter=""):
    """
    Display the deal section for a restaurant.
    
    Args:
        restaurant: Dictionary containing restaurant information
        flyer_existence: Dictionary of pre-checked flyer existence by restaurant name
        text_filter: Text to filter deals by
    """
    st.markdown("<div class='section-header'>Deal</div>", unsafe_allow_html=True)
    
    # Check if a flyer exists for this restaurant (use pre-loaded check)
    has_flyer = flyer_existence[restaurant['name']]
    flyer_path = f"flyers/{restaurant['name'].lower().replace(' ', '_')}_flyer.jpg"
    
    # Check for new column structure first (summarized_deals and detailed_deals)
    if _has_detailed_deals(restaurant):
        _display_detailed_deals(restaurant, has_flyer, flyer_path, text_filter)
    # Fall back to legacy 'deals' column if new structure isn't available
    elif _has_legacy_deals(restaurant):
        _display_legacy_deals(restaurant, has_flyer, flyer_path, text_filter)
    else:
        # No deals available
        st.markdown("<em>No deals available</em>", unsafe_allow_html=True)

def _has_detailed_deals(restaurant):
    """Check if restaurant has detailed deals structure."""
    return ('summarized_deals' in restaurant and restaurant['summarized_deals'] and 
            'detailed_deals' in restaurant and restaurant['detailed_deals'])

def _has_legacy_deals(restaurant):
    """Check if restaurant has legacy deals structure."""
    return 'deals' in restaurant and restaurant['deals']

def _display_detailed_deals(restaurant, has_flyer, flyer_path, text_filter=""):
    """Display deals using the detailed deals structure."""
    summarized_deals = restaurant['summarized_deals']
    detailed_deals = restaurant['detailed_deals']
    
    # Split the deals
    summarized_list = [deal.strip() for deal in summarized_deals.split('->') if deal.strip()]
    detailed_list = [deal.strip() for deal in detailed_deals.split('->') if deal.strip()]
    
    # Make sure we have matching lists (or handle mismatches)
    if len(summarized_list) != len(detailed_list):
        # If lengths don't match, use the shorter length to avoid index errors
        min_length = min(len(summarized_list), len(detailed_list))
        summarized_list = summarized_list[:min_length]
        detailed_list = detailed_list[:min_length]
    
    # Filter deals based on text_filter if provided
    filtered_deals = _filter_detailed_deals(summarized_list, detailed_list, text_filter)
    
    # If we have filtered deals, display them
    if filtered_deals:
        _render_detailed_deals(restaurant, filtered_deals, has_flyer, flyer_path)
    else:
        # No deals match the filter
        _show_no_deals_message(text_filter)

def _filter_detailed_deals(summarized_list, detailed_list, text_filter=""):
    """Filter deals based on text filter."""
    if text_filter:
        text_filter = text_filter.lower()
        return [(i, summary, detail) for i, (summary, detail) in enumerate(zip(summarized_list, detailed_list))
                if text_filter in summary.lower() or text_filter in detail.lower()]
    else:
        # If no text filter, use all deals
        return [(i, summary, detail) for i, (summary, detail) in enumerate(zip(summarized_list, detailed_list))]

def _render_detailed_deals(restaurant, filtered_deals, has_flyer, flyer_path):
    """Render the detailed deals UI."""
    for i, summary, detail in filtered_deals:
        # Create a unique key for this specific deal
        deal_key = f"deal_{restaurant['name'].lower().replace(' ', '_')}_{i}"
        
        # Initialize this deal in session state if not already present
        if deal_key not in st.session_state:
            st.session_state[deal_key] = False
        
        # Create a clickable deal with fire emoji
        if st.button(f"🔥 {summary}", key=f"deal_btn_{deal_key}", use_container_width=True):
            st.session_state[deal_key] = not st.session_state[deal_key]
        
        # If this deal is expanded, show its detailed description
        if st.session_state[deal_key]:
            st.markdown(
                f"""
                <div style="margin-left: 25px; padding: 10px; background-color: #f9f9f9; 
                     border-left: 3px solid #ff4b4b; margin-bottom: 10px;">
                    <div style="color: #555; font-size: 0.9em;">Details:</div>
                    <div>{detail}</div>
                </div>
                """, 
                unsafe_allow_html=True
            )
    
    # Display flyer if available (below all deals)
    if has_flyer and any(st.session_state.get(f"deal_{restaurant['name'].lower().replace(' ', '_')}_{i}", False) 
                         for i, _, _ in filtered_deals):
        st.image(flyer_path, caption="Promotional Flyer", use_container_width =True)

def _display_legacy_deals(restaurant, has_flyer, flyer_path, text_filter=""):
    """Display deals using the legacy deals structure."""
    deals_text = restaurant['deals']
    
    # Split deals by the separator
    if '->' in deals_text:
        _display_multiple_legacy_deals(restaurant, deals_text, has_flyer, flyer_path, text_filter)
    else:
        _display_single_legacy_deal(restaurant, deals_text, has_flyer, flyer_path, text_filter)

def _display_multiple_legacy_deals(restaurant, deals_text, has_flyer, flyer_path, text_filter=""):
    """Display multiple legacy deals."""
    deals_list = [deal.strip() for deal in deals_text.split('->')]
    
    # Filter deals based on text_filter if provided
    filtered_deals = _filter_legacy_deals(deals_list, text_filter)
    
    # If we have filtered deals, display them
    if filtered_deals:
        _render_legacy_deals(restaurant, filtered_deals, has_flyer, flyer_path)
    else:
        # No deals match the filter
        _show_no_deals_message(text_filter)

def _filter_legacy_deals(deals_list, text_filter=""):
    """Filter legacy deals based on text filter."""
    if text_filter:
        text_filter = text_filter.lower()
        return [(i, deal) for i, deal in enumerate(deals_list) if text_filter in deal.lower()]
    else:
        # If no text filter, use all deals
        return [(i, deal) for i, deal in enumerate(deals_list)]

def _render_legacy_deals(restaurant, filtered_deals, has_flyer, flyer_path):
    """Render the legacy deals UI."""
    for i, deal in filtered_deals:
        # Create a unique key for this specific deal
        deal_key = f"deal_{restaurant['name'].lower().replace(' ', '_')}_{i}"
        
        # Initialize this deal in session state if not already present
        if deal_key not in st.session_state:
            st.session_state[deal_key] = False
        
        # Create a clickable deal with fire emoji
        if st.button(f"🔥 {deal}", key=f"deal_btn_{deal_key}", use_container_width=True):
            st.session_state[deal_key] = not st.session_state[deal_key]
        
        # No detailed version available in legacy format, so just highlight when clicked
        if st.session_state[deal_key]:
            st.markdown(
                f"""
                <div style="margin-left: 25px; padding: 10px; background-color: #f9f9f9; 
                     border-left: 3px solid #ff4b4b; margin-bottom: 10px;">
                    {deal}
                </div>
                """, 
                unsafe_allow_html=True
            )
    
    # Display flyer if available (below all deals)
    if has_flyer and any(st.session_state.get(f"deal_{restaurant['name'].lower().replace(' ', '_')}_{i}", False) 
                         for i, _ in filtered_deals):
        st.image(flyer_path, caption="Promotional Flyer", use_column_width=True)

def _display_single_legacy_deal(restaurant, deals_text, has_flyer, flyer_path, text_filter=""):
    """Display a single legacy deal."""
    deal_key = f"deal_{restaurant['name'].lower().replace(' ', '_')}_0"
    
    # Check if the single deal matches the text filter
    show_deal = True
    if text_filter and text_filter.lower() not in deals_text.lower():
        show_deal = False
    
    if show_deal:
        # Initialize this deal in session state if not already present
        if deal_key not in st.session_state:
            st.session_state[deal_key] = False
        
        # Create a clickable deal with fire emoji
        if st.button(f"🔥 {deals_text}", key=f"deal_btn_{deal_key}", use_container_width=True):
            st.session_state[deal_key] = not st.session_state[deal_key]
        
        # Show expanded content if clicked
        if st.session_state[deal_key]:
            st.markdown(
                f"""
                <div style="margin-left: 25px; padding: 10px; background-color: #f9f9f9; 
                     border-left: 3px solid #ff4b4b; margin-bottom: 10px;">
                    {deals_text}
                </div>
                """, 
                unsafe_allow_html=True
            )
            
            # Display flyer if available
            if has_flyer:
                st.image(flyer_path, caption="Promotional Flyer", use_column_width=True)
    else:
        # No deals match the filter
        _show_no_deals_message(text_filter)

def _show_no_deals_message(text_filter=""):
    """Show message when no deals are available or match the filter."""
    if text_filter:
        st.markdown(f"<em>No deals matching '{text_filter}'</em>", unsafe_allow_html=True)
    else:
        st.markdown("<em>No deals available</em>", unsafe_allow_html=True)
