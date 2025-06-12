from OHLC_fetcher import get_historical_ohlc
import pandas as pd

data = get_historical_ohlc(
    exchange="NSE",
    symboltoken="4503",  # replace with real token
    interval="ONE_HOUR",
    from_date="2025-01-06 09:15",
    to_date="2025-06-12 15:30"
)

df = pd.DataFrame(data)

# Rename columns directly
df.columns = ['DateTime', 'Open', 'High', 'Low', 'Close', 'Volume']

# Convert DateTime column to datetime dtype
df['DateTime'] = pd.to_datetime(df['DateTime'])

print(df)

# Save DataFrame to CSV file
csv_file_path = 'Data/historical_data_MPHASIS.csv'  # update path as needed
df.to_csv(csv_file_path, index=False)

print(f"Data saved to {csv_file_path}")
