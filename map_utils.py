import folium

def generate_map(origin_coords, dest_coords, shipment_type):
    lat_center = (origin_coords[0] + dest_coords[0]) / 2
    lon_center = (origin_coords[1] + dest_coords[1]) / 2
    map_obj = folium.Map(location=[lat_center, lon_center], zoom_start=5)

    folium.Marker(origin_coords, tooltip="Origin", icon=folium.Icon(color="green")).add_to(map_obj)
    folium.Marker(dest_coords, tooltip="Destination", icon=folium.Icon(color="red")).add_to(map_obj)

    if shipment_type == "OTR Bulk":
        folium.PolyLine([origin_coords, dest_coords], color="blue", weight=4).add_to(map_obj)
    elif shipment_type == "Iso Tank Bulk":
        folium.PolyLine([origin_coords, dest_coords], color="orange", weight=3, dash_array='5,5').add_to(map_obj)
    elif shipment_type == "Containers Freight":
        folium.PolyLine([origin_coords, dest_coords], color="purple", weight=3).add_to(map_obj)
    elif shipment_type == "LTL & FTL":
        folium.PolyLine([origin_coords, dest_coords], color="gray", weight=2).add_to(map_obj)

    return map_obj._repr_html_()

