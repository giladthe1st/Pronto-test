"""
Utility functions for handling location data and coordinates.
"""
import re
import requests

__all__ = ['extract_coordinates_from_maps_url', 'get_user_location_from_ip', 'get_winnipeg_coordinates_by_area', 'geocode_address']

def extract_coordinates_from_maps_url(maps_url):
    """
    Extract latitude and longitude from a Google Maps URL.
    
    Args:
        maps_url: Google Maps URL string
        
    Returns:
        Tuple of (latitude, longitude) as floats, or (None, None) if not found
    """
    try:
        print(f"Extracting coordinates from URL: {maps_url}")
        
        # Try to extract coordinates from URL format like "...@49.815543,-97.2355725,..."
        coord_match = re.search(r'@([-\d.]+),([-\d.]+)', maps_url)
        if coord_match:
            lat = float(coord_match.group(1))
            lng = float(coord_match.group(2))
            print(f"Found coordinates using @ pattern: {lat}, {lng}")
            return lat, lng
        
        # Try to extract coordinates from URL format like "...!2d-97.1531114!3d49.815565..."
        # Note: In Google Maps URLs, !2d is longitude and !3d is latitude
        lng_match = re.search(r'!2d([-\d.]+)', maps_url)
        lat_match = re.search(r'!3d([-\d.]+)', maps_url)
        if lat_match and lng_match:
            lat = float(lat_match.group(1))
            lng = float(lng_match.group(1))
            print(f"Found coordinates using !2d/!3d pattern: {lat}, {lng}")
            return lat, lng
        
        # Try to extract from geocode format like "...geocode=KVkWYoMXdepSMbQsiUirIZu9&daddr=..."
        # This is more complex and would require additional API calls to resolve
        # For now, we'll handle this by manually mapping some known locations
        if "geocode=" in maps_url:
            print("Found geocode pattern in URL, but need manual mapping")
            
            # Extract the address from the URL if possible
            addr_match = re.search(r'daddr=([^&]+)', maps_url)
            if addr_match:
                address = addr_match.group(1).replace('+', ' ')
                print("Found address in URL: " + address)
                
                # For Winnipeg addresses, we can use approximate coordinates for the city
                if "Winnipeg" in maps_url:
                    # These are approximate coordinates for different areas of Winnipeg
                    if "Pembina" in maps_url:
                        print("Using Pembina area coordinates")
                        return 49.8155, -97.1531  # Pembina area
                    elif "Kenaston" in maps_url:
                        print("Using Kenaston area coordinates")
                        return 49.8372, -97.2055  # Kenaston area
                    elif "Sterling" in maps_url:
                        print("Using Sterling Lyon area coordinates")
                        return 49.8372, -97.2055  # Sterling Lyon area
                    elif "Ness" in maps_url:
                        print("Using Ness avenue area coordinates")
                        return 49.8788, -97.2210  # Ness avenue area
                    elif "Keenlyside" in maps_url:
                        print("Using Keenlyside area coordinates")
                        return 49.9121, -97.0623  # Keenlyside area
                    else:
                        print("Using downtown Winnipeg coordinates")
                        return 49.8951, -97.1384  # Downtown Winnipeg
        
        print("Could not extract coordinates from URL")
        return None, None
    except Exception as e:
        print(f"Error extracting coordinates from maps URL: {e}")
        return None, None

def get_user_location_from_ip():
    """
    Get the user's location based on their IP address using a free geolocation API.
    
    Returns:
        Dictionary containing latitude, longitude, and address information
    """
    try:
        # Use ipinfo.io API to get location data based on IP
        response = requests.get('https://ipinfo.io/json')
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract location data
            if 'loc' in data:
                # Location is provided as "latitude,longitude"
                lat_lng = data['loc'].split(',')
                latitude = float(lat_lng[0])
                longitude = float(lat_lng[1])
                
                # Construct address from available data
                city = data.get('city', '')
                region = data.get('region', '')
                country = data.get('country', '')
                
                if city and region and country:
                    address = f"{city}, {region}, {country}"
                elif city and country:
                    address = f"{city}, {country}"
                else:
                    address = "Current Location"
                
                return {
                    'latitude': latitude,
                    'longitude': longitude,
                    'address': address
                }
    except Exception as e:
        print(f"Error getting location from IP: {e}")
    
    # Fallback to Winnipeg if location can't be determined
    return {
        'latitude': 49.8951,
        'longitude': -97.1384,
        'address': 'Winnipeg City Center (Default)'
    }

def get_winnipeg_coordinates_by_area(location):
    """
    Get approximate coordinates for different areas in Winnipeg.
    
    Args:
        location: String containing location information
        
    Returns:
        Tuple of (latitude, longitude) as floats
    """
    location = location.lower()
    
    if 'pembina' in location:
        return 49.8155, -97.1531
    elif 'kenaston' in location:
        return 49.8372, -97.2055
    elif 'sterling' in location:
        return 49.8372, -97.2055
    elif 'ness' in location:
        return 49.8788, -97.2210
    elif 'keenlyside' in location:
        return 49.9121, -97.0623
    elif 'winnipeg' in location:
        # Default to downtown Winnipeg if we can't be more specific
        return 49.8951, -97.1384
    
    # Default to downtown Winnipeg if no match
    return 49.8951, -97.1384

def geocode_address(address):
    """
    Convert an address string to latitude and longitude coordinates using a geocoding API.
    
    Args:
        address: String containing the address to geocode
        
    Returns:
        Tuple of (latitude, longitude) as floats, or None, None if geocoding fails
    """
    try:
        if not address:
            print("No address provided for geocoding")
            return None, None
            
        # Append "Winnipeg" to the address if it's not already included
        if "winnipeg" not in address.lower() and "manitoba" not in address.lower():
            address = f"{address}, Winnipeg, Manitoba, Canada"
        
        # Use Nominatim geocoding service (OpenStreetMap data)
        # This is a free service with usage limitations
        base_url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": address,
            "format": "json",
            "limit": 1,
            "addressdetails": 1
        }
        
        headers = {
            "User-Agent": "Pronto-Restaurant-App/1.0"  # Required by Nominatim ToS
        }
        
        response = requests.get(base_url, params=params, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                lat = float(data[0]["lat"])
                lon = float(data[0]["lon"])
                print(f"Successfully geocoded address: {address} to {lat}, {lon}")
                return lat, lon
            else:
                print(f"No results found for address: {address}")
        else:
            print(f"Geocoding API error: {response.status_code}")
            
        return None, None
    except Exception as e:
        print(f"Error geocoding address: {e}")
        return None, None
