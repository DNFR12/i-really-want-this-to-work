import folium

def create_route_map_default():
    # default USA-ish view
    return folium.Map(location=[39.5, -98.35], zoom_start=4)

def create_route_map_with_route(shipment_type, origin_coords, dest_coords):
    m = create_route_map_default()

    color = {
        "OTR Bulk": "blue",
        "Iso Tank Bulk": "green",
        "Containers Freight": "purple",
        "LTL & FTL": "orange",
    }.get(shipment_type, "gray")

    folium.Marker(origin_coords, tooltip="Origin", icon=folium.Icon(color="green")).add_to(m)
    folium.Marker(dest_coords, tooltip="Destination", icon=folium.Icon(color="red")).add_to(m)
    folium.PolyLine([origin_coords, dest_coords], color=color, weight=4, dash_array=None if shipment_type=="OTR Bulk" else "8,6").add_to(m)

    return m
