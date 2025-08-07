import folium

def create_route_map(shipment_type, origin_coords, dest_coords):
    route_map = folium.Map(location=origin_coords, zoom_start=5)

    if shipment_type == "OTR Bulk":
        folium.PolyLine([origin_coords, dest_coords], color="blue", weight=5, tooltip="Road Route").add_to(route_map)
    elif shipment_type == "Iso Tank Bulk":
        folium.PolyLine([origin_coords, dest_coords], color="green", weight=5, tooltip="Rail Route").add_to(route_map)
    elif shipment_type in ["Containers Freight", "LTL & FTL"]:
        folium.PolyLine([origin_coords, dest_coords], color="purple", weight=3, dash_array="5, 10", tooltip="Ocean Route").add_to(route_map)

    folium.Marker(origin_coords, tooltip="Origin", icon=folium.Icon(color="green")).add_to(route_map)
    folium.Marker(dest_coords, tooltip="Destination", icon=folium.Icon(color="red")).add_to(route_map)

    return route_map
