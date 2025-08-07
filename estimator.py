import pandas as pd
from utils import load_and_clean_data, filter_data_for_quote
from map_utils import generate_map

DATA = load_and_clean_data("data/")

def get_types():
    return ["OTR Bulk", "Iso Tank Bulk", "Containers Freight", "LTL & FTL"]

def get_origins():
    return sorted(DATA["Origin"].dropna().unique())

def get_destinations():
    return sorted(DATA["Destination"].dropna().unique())

def calculate_quote(shipment_type, origin, destination):
    df = filter_data_for_quote(DATA, shipment_type, origin, destination)
    if df.empty:
        return None
    return round(df["TOTAL"].mean(), 2)

def create_route_map(origin, destination, shipment_type):
    df = filter_data_for_quote(DATA, shipment_type, origin, destination)
    if df.empty:
        return None

    row = df.iloc[0]
    origin_coords = (row["Origin Latitude"], row["Origin Longitude"])
    dest_coords = (row["Destination Latitude"], row["Destination Longitude"])

    return generate_map(origin_coords, dest_coords, shipment_type)

