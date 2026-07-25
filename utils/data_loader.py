import pandas as pd

def load_aqi_data(filepath="data/global_aqi.csv"):
    df = pd.read_csv(filepath, encoding="utf-8-sig", engine="python", on_bad_lines="skip")
    df.columns = df.columns.str.strip()
    return df
def preprocess_aqi_data(df):
    # 1. Remove exact duplicate rows, if any
    df = df.drop_duplicates()

    # 2. Ensure numeric columns are actually numeric (coerce errors to NaN)
    numeric_cols = ['AQI Value', 'CO AQI Value', 'Ozone AQI Value', 'NO2 AQI Value', 'PM2.5 AQI Value', 'lat', 'lng']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # 3. Drop rows where AQI Value itself is missing (core metric, can't analyze without it)
    df = df.dropna(subset=['AQI Value'])

    # 4. Flag rows with missing Country (keep them, just mark clearly)
    df['Country'] = df['Country'].fillna('Unknown')

    # 5. Sanity-check coordinate ranges
    df = df[(df['lat'].between(-90, 90)) & (df['lng'].between(-180, 180))]

    return df
def get_country_rankings(df):
    # Exclude rows with unknown country - doesn't make sense to rank "Unknown"
    country_df = df[df['Country'] != 'Unknown']

    # Group by country, get average AQI value per country
    rankings = country_df.groupby('Country')['AQI Value'].mean().reset_index()

    # Sort from most polluted (highest AQI) to least
    rankings = rankings.sort_values(by='AQI Value', ascending=False)

    return rankings
if __name__ == "__main__":
    raw_df = load_aqi_data("../data/global_aqi.csv")
    print("Before preprocessing:", raw_df.shape)

    clean_df = preprocess_aqi_data(raw_df)
    print("After preprocessing:", clean_df.shape)

    rankings = get_country_rankings(clean_df)
    print("\nTop 10 most polluted countries:")
    print(rankings.head(10))