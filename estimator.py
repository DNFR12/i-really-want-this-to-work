import pandas as pd
from utils import load_data, filter_data_for_quote, calculate_distance

DATA = load_data()

def get_shipment_types():
    return list(DATA.keys())

def get_unique_locations():
    origins = set()
    destinations = set()
    for df in DATA.values():
        origins.update(df['Origin'].dropna().unique())
        destinations.update(df['Destination'].dropna().unique())
    return sorted(origins), sorted(destinations)

def calculate_quote(shipment_type, origin, destination):
    df = DATA.get(shipment_type)
    if df is None:
        return None

    filtered = filter_data_for_quote(df, origin, destination)
    if filtered.empty:
        return None

    avg_total = filtered['Total'].mean()
    dist = calculate_distance(origin, destination)

    return {
        'average_total': round(avg_total, 2),
        'distance_miles': round(dist, 2)
    }
