from datetime import datetime
from connection import obj  # Uses the SmartConnect object from connection.py

def get_historical_ohlc(exchange, symboltoken, interval, from_date, to_date):
    """
    Fetch historical OHLC data from Angel One SmartAPI.
    """
    try:
        params = {
            "exchange": exchange,
            "symboltoken": symboltoken,
            "interval": interval,
            "fromdate": from_date,
            "todate": to_date
        }

        historical_data = obj.getCandleData(params)

        if historical_data.get("status"):
            return historical_data["data"]
        else:
            print("API Error:", historical_data.get("message", "Unknown error"))
            return None

    except Exception as e:
        print("Exception occurred:", str(e))
        return None
