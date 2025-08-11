import pandas as pd
from utils import load_data, filter_data_for_quote, get_distance, STD

# Load and keep in memory
DATA = load_data()

def get_shipment_types():
    return list(DATA.keys())

def get_origins_for_type(shipment_type: str) -> list[str]:
    df = DATA.get(shipment_type)
    if df is None:
        return []
    return sorted(df[STD["origin"]].dropna().unique().tolist())

def get_destinations_for_type(shipment_type: str) -> list[str]:
    df = DATA.get(shipment_type)
    if df is None:
        return []
    return sorted(df[STD["destination"]].dropna().unique().tolist())

def get_unique_locations():
    """If you want global (all types) dropdowns."""
    origins, destinations = set(), set()
    for df in DATA.values():
        origins.update(df[STD["origin"]].dropna().unique())
        destinations.update(df[STD["destination"]].dropna().unique())
    return sorted(origins), sorted(destinations)

def calculate_quote(shipment_type: str, origin: str, destination: str) -> dict | None:
    df = DATA.get(shipment_type)
    if df is None or df.empty:
        return None

    filt = filter_data_for_quote(df, origin, destination)
    if filt.empty:
        return None

    avg_total = round(filt[STD["total"]].mean(), 2)
    # use first row’s coordinates for the map/distance
    row = filt.iloc[0]
    dist = get_distance(row)

    return {
        "shipment_type": shipment_type,
        "origin": origin,
        "destination": destination,
        "average_total": avg_total,
        "distance_miles": dist,
        "origin_coords": (row[STD["olat"]], row[STD["olon"]]),
        "dest_coords": (row[STD["dlat"]], row[STD["dlon"]]),
    }
