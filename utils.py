import pandas as pd

def load_all_data():
    files = {
        "OTR Bulk": "data/otr_bulk.xlsx",
        "Iso Tank Bulk": "data/iso_tank_bulk.xlsx",
        "Containers Freight": "data/containers_freight.xlsx",
        "LTL & FTL": "data/ltl_ftl.xlsx"
    }

    all_data = []

    for shipment_type, path in files.items():
        df = pd.read_excel(path)
        df["Type"] = shipment_type
        all_data.append(df)

    return pd.concat(all_data, ignore_index=True)

def clean_currency(value):
    if isinstance(value, str):
        value = value.replace("$", "").replace(",", "").replace("-", "0").strip()
    try:
        return float(value)
    except:
        return 0.0
