import pandas as pd

def clean_and_combine_data(file_paths):
    df_list = []

    for path in file_paths:
        df = pd.read_excel(path)

        # Normalize headers
        df.columns = [col.strip().title() for col in df.columns]

        # Fix common typos in column headers
        df.rename(columns={
            'Orgin Latitude': 'Origin Latitude',
        }, inplace=True)

        # Ensure all expected columns exist
        expected_cols = [
            'Origin', 'Destination', 'Linehaul', 'Tank Wash', 'Fuel', 'Other', 'Demurrage', 'Total',
            'Origin Latitude', 'Origin Longitude', 'Destination Latitude', 'Destination Longitude'
        ]
        for col in expected_cols:
            if col not in df.columns:
                df[col] = None  # Add missing columns as empty

        # Clean string and numeric columns
        for col in df.select_dtypes(include='object'):
            df[col] = df[col].astype(str).str.strip()
        for col in ['Linehaul', 'Tank Wash', 'Fuel', 'Other', 'Demurrage', 'Total']:
            df[col] = df[col].replace('[\$,]', '', regex=True).replace("-", "0").astype(float)

        df_list.append(df)

    combined = pd.concat(df_list, ignore_index=True)
    return combined.fillna("")
