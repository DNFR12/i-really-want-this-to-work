import pandas as pd
from utils import (
    load_data, filter_data_for_quote, get_distance, STD,
    geocode_city, get_origin_coords, average_per_mile
)

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

def calculate_quote(shipment_type: str, origin: str, destination: str | None, custom_city: str | None) -> dict:
    """
    If `destination` is provided (known lane), return quoted-lane average.
    If not, but `custom_city` is provided, estimate by avg $/mile * distance.
    """
    df = DATA.get(shipment_type)
    if df is None or df.empty:
        return {"error": "No data loaded for this type."}

    # KNOWN LANE PATH
    if destination:
        filt = filter_data_for_quote(df, origin, destination)
        if filt.empty:
            return {"error": "No quoted lane found for this selection."}
        totals = pd.to_numeric(filt[STD["total"]], errors="coerce").dropna()
        if totals.empty:
            return {"error": "Can not Calculate"}
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
            "mode": "quoted",
        }

    # UNKNOWN DESTINATION PATH (custom city)
    if not custom_city:
        return {"error": "Please provide a destination city or select a quoted lane."}

    # geocode custom destination
    dest_coords = geocode_city(custom_city)
    if not dest_coords:
        return {"error": f"Could not geocode '{custom_city}'."}

    # get origin coords from selected type & origin
    origin_coords = get_origin_coords(df, origin)
    if not origin_coords:
        return {"error": f"No coordinates for origin '{origin}' in {shipment_type}."}

    # compute distance
    dist = round(geodesic(origin_coords, dest_coords).miles, 2)

    # avg $/mile from this shipment type
    per_mile = average_per_mile(df)
    if not per_mile:
        return {"error": "Can not Calculate"}

    est_total = round(per_mile * dist, 2)

    return {
        "shipment_type": shipment_type,
        "origin": origin,
        "destination": custom_city,   # show city name for unknown
        "average_total": est_total,
        "distance_miles": dist,
        "origin_coords": origin_coords,
        "dest_coords": dest_coords,
        "mode": "estimated",
        "rate_per_mile": per_mile,
    }
