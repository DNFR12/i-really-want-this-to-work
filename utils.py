import pandas as pd
from geopy.distance import geodesic

STD = {
    "origin": "Origin",
    "destination": "Destination",
    "total": "Total",
    "olat": "Origin Latitude",
    "olon": "Origin Longitude",
    "dlat": "Destination Latitude",
    "dlon": "Destination Longitude",
}

# ... keep the rest of the file as you have it ...

def filter_data_for_quote(df: pd.DataFrame, origin: str, destination: str) -> pd.DataFrame:
    ocol, dcol = STD["origin"], STD["destination"]
    o = origin.strip().lower()
    d = destination.strip().lower()
    return df[
        df[ocol].astype(str).str.strip().str.lower().eq(o)
        & df[dcol].astype(str).str.strip().str.lower().eq(d)
    ]
