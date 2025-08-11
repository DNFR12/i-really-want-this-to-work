import pandas as pd
from geopy.distance import geodesic
from geopy.geocoders import Nominatim

# Standardized column names
STD = {
    "origin": "Origin",
    "destination": "Destination",
    "total": "Total",
    "olat": "Origin Latitude",
    "olon": "Origin Longitude",
    "dlat": "Destination Latitude",
    "dlon": "Destination Longitude",
}

# ---------- existing normalization helpers (unchanged) ----------
def _normalize_cols(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = [str(c).strip().lower() for c in out.columns]
    return out

def _ensure_numeric_money(series: pd.Series) -> pd.Series:
    return (
        series.astype(str)
        .str.replace(r"[,$]", "", regex=True)
        .str.replace("-", "0", regex=False)
        .str.strip()
        .replace({"": "0"})
        .astype(float)
    )

def _remap_columns_by_type(df: pd.DataFrame, shipment_type: str) -> pd.DataFrame:
    raw = _normalize_cols(df)
    colmap = {}

    if "origin" in raw.columns:
        colmap["origin"] = STD["origin"]
    elif "orign" in raw.columns:
        colmap["orign"] = STD["origin"]

    if "destination" in raw.columns:
        colmap["destination"] = STD["destination"]
    elif "designation" in raw.columns:
        colmap["designation"] = STD["destination"]

    if "total" in raw.columns:
        colmap["total"] = STD["total"]

    if "origin latitude" in raw.columns:
        colmap["origin latitude"] = STD["olat"]
    elif "orgin latitude" in raw.columns:
        colmap["orgin latitude"] = STD["olat"]

    if "origin longitude" in raw.columns:
        colmap["origin longitude"] = STD["olon"]

    if "destination latitude" in raw.columns:
        colmap["destination latitude"] = STD["dlat"]
    elif "designation latitude" in raw.columns:
        colmap["designation latitude"] = STD["dlat"]

    if "destination longitude" in raw.columns:
        colmap["destination longitude"] = STD["dlon"]
    elif "designation longitude" in raw.columns:
        colmap["designation longitude"] = STD["dlon"]

    norm = raw.rename(columns=colmap)
    for need in STD.values():
        if need not in norm.columns:
            norm[need] = pd.NA

    norm[STD["total"]] = _ensure_numeric_money(norm[STD["total"]]).fillna(0.0)

    for col in [STD["origin"], STD["destination"]]:
        norm[col] = norm[col].astype(str).str.strip()

    for col in [STD["olat"], STD["olon"], STD["dlat"], STD["dlon"]]:
        norm[col] = pd.to_numeric(norm[col], errors="coerce")

    norm = norm[[STD["origin"], STD["destination"], STD["total"],
                 STD["olat"], STD["olon"], STD["dlat"], STD["dlon"]]].copy()
    norm["Type"] = shipment_type
    return norm

def load_data() -> dict:
    files = {
        "OTR Bulk": "data/otr_bulk.xlsx",
        "Iso Tank Bulk": "data/iso_tank_bulk.xlsx",
        "Containers Freight": "data/containers_freight.xlsx",
        "LTL & FTL": "data/ltl_ftl.xlsx",
    }
    out = {}
    for stype, path in files.items():
        df = pd.read_excel(path)
        out[stype] = _remap_columns_by_type(df, stype)
    return out

def filter_data_for_quote(df: pd.DataFrame, origin: str, destination: str) -> pd.DataFrame:
    ocol, dcol = STD["origin"], STD["destination"]
    o = origin.strip().lower()
    d = destination.strip().lower()
    return df[
        df[ocol].astype(str).str.strip().str.lower().eq(o)
        & df[dcol].astype(str).str.strip().str.lower().eq(d)
    ]

def get_distance(row: pd.Series) -> float | None:
    try:
        o = (float(row[STD["olat"]]), float(row[STD["olon"]]))
        d = (float(row[STD["dlat"]]), float(row[STD["dlon"]]))
        if any(pd.isna(list(o) + list(d))):
            return None
        return round(geodesic(o, d).miles, 2)
    except Exception:
        return None

# ---------- NEW: geocoding + per-mile helpers ----------
_geocoder = Nominatim(user_agent="freight-estimator", timeout=8)

def geocode_city(city_name: str) -> tuple[float, float] | None:
    """Return (lat, lon) for a city name, or None if not found."""
    if not city_name or not city_name.strip():
        return None
    try:
        g = _geocoder.geocode(city_name.strip())
        if not g:
            return None
        return (g.latitude, g.longitude)
    except Exception:
        return None

def get_origin_coords(df: pd.DataFrame, origin: str) -> tuple[float, float] | None:
    """Pick first row matching the origin and return its origin coords."""
    mask = df[STD["origin"]].astype(str).str.strip().str.lower().eq(origin.strip().lower())
    if not mask.any():
        return None
    row = df.loc[mask].iloc[0]
    lat, lon = row[STD["olat"]], row[STD["olon"]]
    if pd.isna(lat) or pd.isna(lon):
        return None
    return (float(lat), float(lon))

def average_per_mile(df: pd.DataFrame) -> float | None:
    """
    Compute average Total-per-mile across all rows with valid coords & distance > 0.
    """
    per_miles = []
    for _, r in df.iterrows():
        o_lat, o_lon = r[STD["olat"]], r[STD["olon"]]
        d_lat, d_lon = r[STD["dlat"]], r[STD["dlon"]]
        if pd.isna(o_lat) or pd.isna(o_lon) or pd.isna(d_lat) or pd.isna(d_lon):
            continue
        dist = geodesic((o_lat, o_lon), (d_lat, d_lon)).miles
        if dist and dist > 0:
            per_miles.append(float(r[STD["total"]]) / dist)
    if not per_miles:
        return None
    return round(sum(per_miles) / len(per_miles), 4)
