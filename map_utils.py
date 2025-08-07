import folium
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="freight-app")

def geocode(city):
    location = geolocator.geocode(city)
    return (location.latitude, location.longitude) if location else (None, None)

def create_map(origin=None, destination=None, shipment_type=None):
    # Default location: central U.S.
    fmap = folium.Map(location=[39.5, -98.35], zoom_start=4)

    if origin and destination:
        orig_coords = geocode(origin)
        dest_coords = geocode(destination)

        if orig_coords and dest_coords:
            folium.Marker(orig_coords, tooltip='Origin: ' + origin).add_to(fmap)
            folium.Marker(dest_coords, tooltip='Destination: ' + destination).add_to(fmap)

            if shipment_type == "OTR Bulk":
                folium.PolyLine([orig_coords, dest_coords], color='blue', weight=4).add_to(fmap)
            elif shipment_type == "Iso Tank Bulk":
                folium.PolyLine([orig_coords, dest_coords], color='green', weight=4, dash_array='10').add_to(fmap)
            elif shipment_type == "Containers Freight":
                folium.PolyLine([orig_coords, dest_coords], color='purple', weight=3, dash_array='1').add_to(fmap)
            elif shipment_type == "LTL FTL":
                folium.PolyLine([orig_coords, dest_coords], color='orange', weight=2, dash_array='5').add_to(fmap)

    return fmap._repr_html_()
