def average_per_mile(df: pd.DataFrame, trim_top_pct: float = 0.0) -> float | None:
    """
    Return the average Total-per-mile for this shipment type.
    - Uses geodesic distance between each row's coords.
    - Skips rows with missing coords or zero distance.
    - If trim_top_pct > 0, excludes the top X% highest $/mi (outliers).
      e.g., trim_top_pct=0.15 drops the top 15% most expensive per-mile rows.
    """
    per_miles = []

    for _, r in df.iterrows():
        o_lat, o_lon = r[STD["olat"]], r[STD["olon"]]
        d_lat, d_lon = r[STD["dlat"]], r[STD["dlon"]]
        if pd.isna(o_lat) or pd.isna(o_lon) or pd.isna(d_lat) or pd.isna(d_lon):
            continue
        try:
            dist = geodesic((float(o_lat), float(o_lon)), (float(d_lat), float(d_lon))).miles
        except Exception:
            continue
        if dist and dist > 0:
            try:
                total = float(r[STD["total"]])
            except Exception:
                continue
            per_miles.append(total / dist)

    if not per_miles:
        return None

    s = pd.Series(per_miles, dtype=float)

    if trim_top_pct and 0 < trim_top_pct < 1:
        cutoff = s.quantile(1 - trim_top_pct)
        trimmed = s[s <= cutoff]
        if not trimmed.empty:
            return round(trimmed.mean(), 4)

    return round(s.mean(), 4)
