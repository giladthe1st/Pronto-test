"""
Menu display functionality for restaurant UI.
"""
import streamlit as st

def display_menu_section(restaurant):
    """
    Display the menu section for a restaurant.
    
    Args:
        restaurant: Dictionary containing restaurant information
    """
    st.markdown("<div class='section-header'>Menu</div>", unsafe_allow_html=True)
    
    # Create a unique key for this restaurant's menu expander
    menu_key = f"menu_{restaurant['name'].lower().replace(' ', '_')}"
    
    # Initialize this menu in session state if not already present
    if menu_key not in st.session_state:
        st.session_state[menu_key] = False
    
    # Create a toggle function for this menu with proper closure
    def toggle_menu(key=menu_key):
        st.session_state[key] = not st.session_state[key]
    
    # Check if menu URL is available
    menu_url = restaurant.get('menu_url', '')
    has_menu = bool(menu_url)
    
    # Create an expandable menu section with toggle button
    button_text = "View Menu"
    if st.session_state[menu_key]:
        button_text = "Hide Menu"
    
    # Use a more efficient button implementation with a different key for the button
    st.button(
        button_text, 
        key=f"btn_{menu_key}", 
        help="Click to expand/collapse", 
        on_click=toggle_menu,
        use_container_width=True,
        disabled=not has_menu
    )
    
    # Show expanded content if this menu is expanded
    if st.session_state[menu_key]:
        st.markdown("<div class='expanded-content'>", unsafe_allow_html=True)
        
        if has_menu:
            st.markdown("<strong>Menu Information:</strong>", unsafe_allow_html=True)
            st.markdown(f"<a href='{menu_url}' target='_blank'>Open Full Menu in New Tab</a>", unsafe_allow_html=True)
            
            # Use lazy loading for iframe to improve performance
            # Only load iframe when menu is expanded
            st.components.v1.iframe(
                menu_url, 
                height=300, 
                scrolling=True
            )
        else:
            st.markdown("<em>Menu not available for this restaurant</em>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    elif not has_menu:
        st.markdown("<em>Menu not available for this restaurant</em>", unsafe_allow_html=True)
