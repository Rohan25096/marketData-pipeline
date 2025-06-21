import time
import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf
from database_connection import supabase

def fetch_candle_data():
    try:
        response = supabase.table("live_data").select("*").order("timestamp", desc=False).execute()
        records = response.data

        # Convert to DataFrame
        df = pd.DataFrame(records)

        # Ensure Volume is float
        df['volume'] = df['volume'].astype(float)

        # Convert timestamp to datetime and set as index
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)

        # Sort to be safe
        df.sort_index(inplace=True)

        return df

    except Exception as e:
        print(f"[Error] Failed to fetch or prepare data: {e}")
        return pd.DataFrame()

def main():
    while True:
        df = fetch_candle_data()
        if df.empty or len(df) < 1:
            print("[Info] No candle data to display.")
            time.sleep(5)
            continue

        # Select only necessary columns
        df_plot = df[['open', 'high', 'low', 'close', 'volume']].tail(40)

        # Plot compact candlestick chart
        fig, axlist = mpf.plot(
            df_plot,
            type='candle',
            style=mpf.make_mpf_style(
                base_mpl_style='dark_background',
                rc={'font.size': 9}
            ),
            figsize=(9, 4),
            tight_layout=True,
            update_width_config=dict(candle_linewidth=0.8, candle_width=0.4),
            returnfig=True
        )

        plt.pause(5)
        plt.close(fig)

if __name__ == "__main__":
    main()
