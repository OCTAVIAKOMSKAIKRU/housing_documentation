# map_utils.py
from geopy.geocoders import Nominatim
import folium

def geocode_address(address):
    """
    Convert an address (or suburb, city) into (latitude, longitude).
    Uses GeoPy with Nominatim (OpenStreetMap) under the hood:contentReference[oaicite:19]{index=19}.
    """
    geolocator = Nominatim(user_agent="property24_app")
    try:
        loc = geolocator.geocode(address)
        if loc:
            return loc.latitude, loc.longitude
    except Exception:
        pass
    return None, None

def create_map(listings_df):
    """
    Create a folium map with markers for each listing in the dataframe.
    Assumes listings_df has columns 'Suburb', 'City', and optionally 'Title'.
    """
    # Geocode each unique suburb (cache this in real app)
    coords = {}
    for _, row in listings_df.iterrows():
        place = f"{row['Suburb']}, {row['City']}"
        if place not in coords:
            coords[place] = geocode_address(place)
    # Initialize map (example location centered on South Africa)
    m = folium.Map(location=[-30.0, 25.0], zoom_start=5)
    for place, (lat, lon) in coords.items():
        if lat and lon:
            folium.Marker([lat, lon], popup=place).add_to(m)
    return m

# In Streamlit, you could use st.map() or st.pydeck_chart to display coordinates.
# Streamlit’s st.map can plot points given latitude/longitude columns (auto-centers map):contentReference[oaicite:20]{index=20}.