import folium
import requests

# Shipment type groups
ROAD_TYPES = {"OTR Bulk", "LTL & FTL"}
RAIL_TYPES = {"Iso Tank Bulk"}
OCEAN_TYPES = {"Containers Freight"}

def _base_map():
    # Fullscreen map, no scroll on page; folium container will be 100% width/height
    return folium.Map(
        location=[39.5, -98.35],  # CONUS center
        zoom_start=4,
        tiles="OpenStreetMap",
        control_scale=True,
        width="100%",
        height="100%",
    )

def _fit_bounds(m, a, b):
    # Auto-zoom to show both endpoints
    m.fit_bounds([a, b])

def _osrm_route(origin_coords, dest_coords):
    """
    Snap a driving route using OSRM public server.
    Returns list[(lat, lon)] or None on failure.
    """
    try:
        (olat, olon) = origin_coords
        (dlat, dlon) = dest_coords
        url = (
            "https://router.project-osrm.org/route/v1/driving/"
            f"{olon},{olat};{dlon},{dlat}?overview=full&geometries=geojson"
        )
        r = requests.get(url, timeout=8)
        r.raise_for_status()
        data = r.json()
        routes = data.get("routes")
        if not routes:
            return None
        coords = routes[0]["geometry"]["coordinates"]  # [lon, lat]
        return [(lat, lon) for lon, lat in coords]
    except Exception:
        return None

def create_route_map_default():
    # Fullscreen default
    return _base_map()

def create_route_map_with_route(shipment_type, origin_coords, dest_coords):
    m = _base_map()

    # Markers
    folium.Marker(origin_coords, tooltip="Origin", icon=folium.Icon(color="green")).add_to(m)
    folium.Marker(dest_coords, tooltip="Destination", icon=folium.Icon(color="red")).add_to(m)

    color = {
        "OTR Bulk": "blue",
        "LTL & FTL": "blue",
        "Iso Tank Bulk": "green",
        "Containers Freight": "purple",
    }.get(shipment_type, "gray")

    # Draw route
    if shipment_type in ROAD_TYPES:
        # Try snapped road route; fallback to straight line
        snapped = _osrm_route(origin_coords, dest_coords)
        path = snapped if snapped else [origin_coords, dest_coords]
        folium.PolyLine(path, color=color, weight=5, opacity=0.9).add_to(m)

    elif shipment_type in RAIL_TYPES:
        # Simple dashed line to suggest rail corridor (we’re not routing rail)
        folium.PolyLine([origin_coords, dest_coords], color=color, weight=5, dash_array="8,6").add_to(m)

    elif shipment_type in OCEAN_TYPES:
        # Thin dotted to suggest sea lane
        folium.PolyLine([origin_coords, dest_coords], color=color, weight=4, dash_array="2,8").add_to(m)

    else:
        folium.PolyLine([origin_coords, dest_coords], color=color, weight=4).add_to(m)

    # Auto-zoom to route
    _fit_bounds(m, origin_coords, dest_coords)
    return m
