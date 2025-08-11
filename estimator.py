import pandas as pd
from utils import load_data, filter_data_for_quote, get_distance, STD

# Load and normalize once
DATA = load_data()

def get_shipment_types():
    return list(DATA.keys())

def get_origins_for_type(shipment_type: str) -> list[str]:
    df = DATA.get(shipment_type)
    if df is None or df.empty:
        return []
    return sorted(df[STD["origin"]].dropna().unique().tolist())

def get_destinations_for_type_origin(shipment_type: str, origin: str) -> list[str]:
    df = DATA.get(shipment_type)
    if df is None or df.empty or not origin:
        return []
    mask = df[STD["origin"]].astype(str).str.strip().str.lower().eq(origin.strip().lower())
    dests = df.loc[mask, STD["destination"]].dropna().unique().tolist()
    return sorted(dests)

def calculate_quote(shipment_type: str, origin: str, destination: str) -> dict:
    df = DATA.get(shipment_type)
    if df is None or df.empty:
        return {"error": "No data loaded for this type."}

    filt = filter_data_for_quote(df, origin, destination)
    if filt.empty:
        return {"error": "No quoted lane found for this selection."}

    totals = pd.to_numeric(filt[STD["total"]], errors="coerce").dropna()
    if totals.empty:
        return {"error": "Can not Calculate"}  # required fallback

    avg_total = round(totals.mean(), 2)
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
