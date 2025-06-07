from OHLC_fetcher import get_historical_ohlc
import pandas as pd

data = get_historical_ohlc(
    exchange="NSE",
    symboltoken="404",  # replace with real token
    interval="FIVE_MINUTE",
    from_date="2025-06-06 09:15",
    to_date="2025-06-06 15:30"
)

df = pd.DataFrame(data)

#Rename columns directly
df.columns = ['DateTime', 'Open', 'High', 'Low', 'Close', 'Volume']
df['DateTime'] = pd.to_datetime(df['DateTime'])

print(df)
