import pandas as pd
import os

def clean_column(df, col):
    if col in df.columns:
        df[col] = df[col].replace('[\$,]', '', regex=True).replace("-", "0").astype(float)
    return df

def load_and_clean_data(folder_path):
    combined_df = pd.DataFrame()

    for file in os.listdir(folder_path):
        if file.endswith(".xlsx"):
            df = pd.read_excel(os.path.join(folder_path, file))
            for col in ["LINEHAUL", "TANK WASH", "FUEL", "OTHER", "Demurrage", "TOTAL"]:
                df = clean_column(df, col)
            if "FUEL" in df.columns:
                df["FUEL_PCT"] = df["FUEL"] / 100 if df["FUEL"].max() <= 1 else df["FUEL"]
            combined_df = pd.concat([combined_df, df], ignore_index=True)

    return combined_df

def filter_data_for_quote(data, shipment_type, origin, destination):
    return data[
        (data["Type"] == shipment_type) &
        (data["Origin"] == origin) &
        (data["Destination"] == destination)
    ]

