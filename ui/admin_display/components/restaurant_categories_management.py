"""
Restaurant categories management component for admin interface.
"""
import streamlit as st
from database.supabase_client import get_supabase_client
from ui.admin_display.components.utils import display_data_table, get_table_data, get_dropdown_options

def manage_restaurant_categories():
    """Display restaurant categories management interface."""
    st.header("Restaurant Categories")
    
    # Display existing restaurant categories
    display_existing_restaurant_categories()
    
    # Get options for dropdowns
    restaurant_options = get_dropdown_options('Restaurants', 'id', 'name')
    category_options = get_dropdown_options('Categories', 'id', 'name')
    
    # Form to add a new restaurant category
    display_add_restaurant_category_form(restaurant_options, category_options)

def display_existing_restaurant_categories():
    """Display existing restaurant categories with restaurant names."""
    try:
        # Get existing restaurant categories
        restaurant_categories = get_table_data('Restaurant_Categories')
        
        if restaurant_categories:
            # Enhance with restaurant names and category types
            enhance_restaurant_categories_with_names_and_types(restaurant_categories)
            display_data_table(restaurant_categories, "Existing Restaurant Categories")
    except Exception as e:
        st.error(f"Error displaying restaurant categories: {e}")

def enhance_restaurant_categories_with_names_and_types(restaurant_categories):
    """
    Add restaurant names and category types to restaurant categories data.
    
    Args:
        restaurant_categories (list): List of restaurant category dictionaries
    """
    try:
        client = get_supabase_client(use_service_role=True)
        
        # Get unique restaurant IDs
        restaurant_ids = list(set([rc['restaurant_id'] for rc in restaurant_categories]))
        
        # Get unique category IDs
        category_ids = list(set([rc['category_id'] for rc in restaurant_categories]))
        
        if restaurant_ids:
            # Get restaurant names for those IDs
            restaurant_names_response = client.table('Restaurants').select('id, name').in_('id', restaurant_ids).execute()
            restaurant_names = {r['id']: r['name'] for r in restaurant_names_response.data}
            
            # Add restaurant names to the data
            for rc in restaurant_categories:
                rc['restaurant_name'] = restaurant_names.get(rc['restaurant_id'], f"Restaurant {rc['restaurant_id']}")
        
        if category_ids:
            # Get category types for those IDs
            category_types_response = client.table('Categories').select('id, name').in_('id', category_ids).execute()
            category_types = {c['id']: c['name'] for c in category_types_response.data}
            
            # Add category types to the data
            for rc in restaurant_categories:
                rc['category_type'] = category_types.get(rc['category_id'], f"Category {rc['category_id']}")
    except Exception as e:
        st.warning(f"Could not load restaurant names or category types: {e}")

def display_add_restaurant_category_form(restaurant_options, category_options):
    """
    Display form for adding a new restaurant category.
    
    Args:
        restaurant_options (dict): Dictionary of restaurant names to ids
        category_options (dict): Dictionary of category names to ids
    """
    with st.expander("Add Restaurant Category"):
        with st.form("add_restaurant_category_form"):
            # Restaurant selection
            if restaurant_options:
                selected_restaurant = st.selectbox("Restaurant", list(restaurant_options.keys()))
                restaurant_id = restaurant_options[selected_restaurant]
            else:
                st.warning("No restaurants available. Please add restaurants first.")
                selected_restaurant = None
                restaurant_id = None
            
            # Category selection
            if category_options:
                selected_category = st.selectbox("Category", list(category_options.keys()))
                category_id = category_options[selected_category]
            else:
                st.warning("No categories available. Please add categories first.")
                selected_category = None
                category_id = None
            
            submitted = st.form_submit_button("Add Restaurant Category")
            if submitted:
                handle_restaurant_category_submission(
                    restaurant_id, category_id, selected_restaurant, selected_category
                )

def handle_restaurant_category_submission(restaurant_id, category_id, selected_restaurant, selected_category):
    """
    Handle the submission of a new restaurant category form.
    
    Args:
        restaurant_id: ID of the selected restaurant
        category_id: ID of the selected category
        selected_restaurant: Name of the selected restaurant (for display)
        selected_category: Name of the selected category (for display)
    """
    if not restaurant_id or not category_id:
        st.error("Please ensure both restaurant and category are selected.")
        return
    
    # Check if this restaurant-category pair already exists
    if check_existing_restaurant_category(restaurant_id, category_id, selected_restaurant, selected_category):
        return
    
    # Create and insert the restaurant category
    insert_restaurant_category(restaurant_id, category_id, selected_restaurant, selected_category)

def check_existing_restaurant_category(restaurant_id, category_id, selected_restaurant, selected_category):
    """
    Check if a restaurant-category pair already exists.
    
    Args:
        restaurant_id: ID of the selected restaurant
        category_id: ID of the selected category
        selected_restaurant: Name of the selected restaurant (for display)
        selected_category: Name of the selected category (for display)
        
    Returns:
        bool: True if exists, False otherwise
    """
    try:
        client = get_supabase_client(use_service_role=True)
        check_response = client.table('Restaurant_Categories').select('*')\
            .eq('restaurant_id', restaurant_id)\
            .eq('category_id', category_id)\
            .execute()
        
        if check_response.data:
            st.warning(f"Restaurant {selected_restaurant} is already associated with category {selected_category}.")
            return True
        return False
    except Exception as e:
        st.error(f"Error checking for existing restaurant category: {e}")
        return True

def insert_restaurant_category(restaurant_id, category_id, selected_restaurant, selected_category):
    """
    Insert a new restaurant-category association.
    
    Args:
        restaurant_id: ID of the selected restaurant
        category_id: ID of the selected category
        selected_restaurant: Name of the selected restaurant (for display)
        selected_category: Name of the selected category (for display)
    """
    try:
        client = get_supabase_client(use_service_role=True)
        
        # Create restaurant category data
        restaurant_category_data = {
            "restaurant_id": restaurant_id,
            "category_id": category_id
        }
        
        # Try to insert the restaurant category
        insert_response = client.table('Restaurant_Categories').insert(restaurant_category_data).execute()
        if insert_response.data:
            st.success(f"Category {selected_category} added to {selected_restaurant} successfully!")
            st.rerun()  # Refresh the page
        else:
            st.error("Failed to add restaurant category.")
    except Exception as e:
        handle_restaurant_category_error(e, selected_restaurant)

def handle_restaurant_category_error(error, selected_restaurant):
    """
    Handle errors when inserting restaurant categories.
    
    Args:
        error: The exception that occurred
        selected_restaurant: Name of the selected restaurant (for display)
    """
    error_msg = str(error)
    if "duplicate key value" in error_msg and "Restaurant_Categories_pkey" in error_msg:
        st.warning("This restaurant-category association already exists.")
    elif "duplicate key value" in error_msg and "Restaurant_Categories_restaurant_id_key" in error_msg:
        st.warning(f"Restaurant {selected_restaurant} can only be associated with one category due to database constraints.")
        st.info("To associate with multiple categories, the database schema needs to be modified to remove the unique constraint on restaurant_id.")
    else:
        st.error(f"Error adding restaurant category: {error}")
