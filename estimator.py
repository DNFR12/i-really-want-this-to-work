import pandas as pd
from utils import load_all_data, clean_currency
from geopy.distance import geodesic

DATA = load_all_data()

def get_shipment_types():
    return ["OTR Bulk", "Iso Tank Bulk", "Containers Freight", "LTL & FTL"]

def get_known_destinations():
    if "Destination" in DATA.columns:
        return sorted(DATA["Destination"].dropna().unique())
    return []

def estimate_freight(shipment_type, origin, destination):
    df = DATA[
        (DATA["Type"] == shipment_type)
        & (DATA["Origin"] == origin)
        & (DATA["Destination"] == destination)
    ]

    if df.empty:
        return {
            "error": "No matching lane found.",
            "shipment_type": shipment_type
        }

    total_values = df["Total"].apply(clean_currency)
    avg_total = round(total_values.mean(), 2)

    first_row = df.iloc[0]
    origin_coords = (first_row["Origin Latitude"], first_row["Origin Longitude"])
    dest_coords = (first_row["Destination Latitude"], first_row["Destination Longitude"])
    distance = round(geodesic(origin_coords, dest_coords).miles, 2)

    return {
        "origin": origin,
        "destination": destination,
        "shipment_type": shipment_type,
        "quote": avg_total,
        "distance": distance,
        "origin_coords": origin_coords,
        "dest_coords": dest_coords
    }
