import pandas as pd
from geopy.distance import geodesic

def load_data():
    return {
        "OTR Bulk": pd.read_excel("data/otr_bulk.xlsx"),
        "Iso Tank Bulk": pd.read_excel("data/iso_tank_bulk.xlsx"),
        "Containers Freight": pd.read_excel("data/containers_freight.xlsx"),
        "LTL FTL": pd.read_excel("data/ltl_ftl.xlsx"),
    }

def filter_data_for_quote(df, origin, destination):
    return df[
        (df['Origin'].str.strip().str.lower() == origin.strip().lower()) &
        (df['Destination'].str.strip().str.lower() == destination.strip().lower())
    ]

def calculate_distance(origin_city, destination_city):
    from map_utils import geocode
    orig_coords = geocode(origin_city)
    dest_coords = geocode(destination_city)
    if None in orig_coords or None in dest_coords:
        return 0
    return geodesic(orig_coords, dest_coords).miles
