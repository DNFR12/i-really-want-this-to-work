import pandas as pd
from geopy.distance import geodesic

# Standardized column names we enforce across all files
STD = {
    "origin": "Origin",
    "destination": "Destination",
    "total": "Total",
    "olat": "Origin Latitude",
    "olon": "Origin Longitude",
    "dlat": "Destination Latitude",
    "dlon": "Destination Longitude",
}

def _normalize_cols(df: pd.DataFrame) -> pd.DataFrame:
    """Lowercase & strip headers for robust renaming."""
    out = df.copy()
    out.columns = [str(c).strip().lower() for c in out.columns]
    return out

def _ensure_numeric_money(series: pd.Series) -> pd.Series:
    """Turn money-like strings into floats safely."""
    return (
        series.astype(str)
        .str.replace(r"[,$]", "", regex=True)
        .str.replace("-", "0", regex=False)
        .str.strip()
        .replace({"": "0"})
        .astype(float)
    )

def _remap_columns_by_type(df: pd.DataFrame, shipment_type: str) -> pd.DataFrame:
    """
    Map raw headers -> standard names for each of your four layouts.
    Always returns a frame with STD columns (creating missing as NA).
    """
    raw = _normalize_cols(df)
    colmap = {}

    # Origin
    if "origin" in raw.columns:
        colmap["origin"] = STD["origin"]
    elif "orign" in raw.columns:
        colmap["orign"] = STD["origin"]
    # ignore "o port"

    # Destination (sometimes "designation")
    if "destination" in raw.columns:
        colmap["destination"] = STD["destination"]
    elif "designation" in raw.columns:
        colmap["designation"] = STD["destination"]
    # ignore "d port"

    # Total
    if "total" in raw.columns:
        colmap["total"] = STD["total"]

    # Lat/Lon (and typo: "orgin latitude")
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

    # Ensure all standard columns exist
    for need in STD.values():
        if need not in norm.columns:
            norm[need] = pd.NA

    # Clean money
    norm[STD["total"]] = _ensure_numeric_money(norm[STD["total"]]).fillna(0.0)

    # Clean strings
    for col in [STD["origin"], STD["destination"]]:
        norm[col] = norm[col].astype(str).str.strip()

    # Lat/Lon to numeric
    for col in [STD["olat"], STD["olon"], STD["dlat"], STD["dlon"]]:
        norm[col] = pd.to_numeric(norm[col], errors="coerce")

    # Keep only standard columns + Type
    norm = norm[[STD["origin"], STD["destination"], STD["total"],
                 STD["olat"], STD["olon"], STD["dlat"], STD["dlon"]]].copy()
    norm["Type"] = shipment_type
    return norm

def load_data() -> dict:
    """
    Read the four files and normalize to a consistent schema.
    Returns a dict: { shipment_type: DataFrame }
    """
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
    """Safe, case-insensitive matching on normalized columns."""
    ocol, dcol = STD["origin"], STD["destination"]
    o = origin.strip().lower()
    d = destination.strip().lower()
    return df[
        df[ocol].astype(str).str.strip().str.lower().eq(o)
        & df[dcol].astype(str).str.strip().str.lower().eq(d)
    ]

def get_distance(row: pd.Series) -> float | None:
    """Compute geodesic miles from a normalized row (returns None if coords missing)."""
    try:
        o = (float(row[STD["olat"]]), float(row[STD["olon"]]))
        d = (float(row[STD["dlat"]]), float(row[STD["dlon"]]))
        if any(pd.isna(list(o) + list(d))):
            return None
        return round(geodesic(o, d).miles, 2)
    except Exception:
        return None
