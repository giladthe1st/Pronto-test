# Restaurant Finder App

A Streamlit web application that displays restaurant information including logos, names, deals, menus, reviews, locations, and directions.

## Features

- Display restaurant information in a clean, card-based layout
- Each restaurant entry includes:
  - Restaurant logo
  - Name with hyperlink to the restaurant website
  - Current deals/promotions
  - Link to menu
  - Reviews
  - Location information
  - Distance
  - Link to Google Maps for directions
- Filter restaurants by distance
- Support for multiple data sources (currently CSV, with Google Sheets integration planned)

## Setup and Installation

1. Clone this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Run the Streamlit app:

```bash
streamlit run app.py
```

## Data Sources

### CSV File

The app currently uses a sample CSV file (`sample_restaurants.csv`) as its data source. You can modify this file or create your own with the following columns:

- `name`: Restaurant name
- `logo_url`: URL to the restaurant's logo image
- `website`: Restaurant website URL
- `deals`: Current deals or promotions
- `menu_url`: URL to the restaurant's menu
- `reviews`: Review information (e.g., "4.5/5 (120 reviews)")
- `location`: Restaurant address
- `distance`: Distance from a reference point (e.g., "1.2 miles")
- `maps_url`: Google Maps URL for directions

### Google Sheets (Coming Soon)

Integration with Google Sheets is planned for a future update.

## Customization

You can customize the app by:

1. Modifying the CSS in the `app.py` file
2. Adding additional filters in the sidebar
3. Extending the `DataHandler` class to support more data sources

## Future Enhancements

- Google Sheets integration
- Search functionality
- More filtering options (by cuisine, price range, etc.)
- User reviews and ratings
- Integration with restaurant APIs (e.g., Yelp, Google Places)
