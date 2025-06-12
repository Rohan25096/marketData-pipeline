from OHLC_fetcher import get_historical_ohlc
import pandas as pd
def get_hist_ohlc(exchange,token_no,interval,from_date,to_date):
    
    data = get_historical_ohlc(
        exchange=exchange,
        symboltoken=token_no,  # replace with real token
        interval=interval,
        from_date=from_date,
        to_date=to_date
    )

    df = pd.DataFrame(data)

    # Rename columns directly
    df.columns = ['DateTime', 'Open', 'High', 'Low', 'Close', 'Volume']

    # Convert DateTime column to datetime dtype
    df['DateTime'] = pd.to_datetime(df['DateTime'])

    print(df)

    # Save DataFrame to CSV file
    csv_file_path = f'Data/historical_data_{token_no}.csv'  # update path as needed
    df.to_csv(csv_file_path, index=False)

    print(f"Data saved to {csv_file_path}")

get_hist_ohlc(exchange="NSE",
        token_no="2263",  # replace with real token
        interval="FIFTEEN_MINUTE",
        from_date="2025-06-01 09:15",
        to_date="2025-06-12 15:30")