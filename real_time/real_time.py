from SmartApi import SmartConnect
from dotenv import load_dotenv
from logzero import logger
from database_connection import supabase
import pyotp
import os
import json
import http.client
import time
from datetime import datetime, timezone, timedelta

# --- Load credentials ---
load_dotenv(dotenv_path="Your path to the .env file")

api_key     = os.getenv("API_KEY")
CLIENT_CODE = os.getenv("CLIENT_CODE")
pwd         = os.getenv("PASSWORD")
totp_secret = os.getenv("TOTP_SECRET")
local_ip    = os.getenv("X-ClientLocalIP")
public_ip   = os.getenv("X-ClientPublicIP")
mac_add     = os.getenv("X-MACAddress")

# --- Define timezone ---
IST = timezone(timedelta(hours=5, minutes=30))

# --- Create session ---
obj = SmartConnect(api_key)
session = obj.generateSession(CLIENT_CODE, pwd, pyotp.TOTP(totp_secret).now())

if not session['status']:
    logger.error(session)
    exit()

authToken   = session['data']['jwtToken']
refreshToken= session['data']['refreshToken']
feedToken   = obj.getfeedToken()
obj.generateToken(refreshToken)

print("[INFO] Real-time candle fetcher started...")

# --- Main Loop ---
while True:
    try:
        now = datetime.now(IST)
        from_time = (now - timedelta(minutes=5)).strftime("2025-06-18 12:05")
        to_time = now.strftime("2025-06-18 12:10")

        conn = http.client.HTTPSConnection("apiconnect.angelone.in")
        headers = {
            'X-PrivateKey': api_key,
            'Accept': 'application/json',
            'X-SourceID': 'WEB',
            'X-ClientLocalIP': local_ip,
            'X-ClientPublicIP': public_ip,
            'X-MACAddress': mac_add,
            'X-UserType': 'USER',
            'Authorization': authToken,
            'Content-Type': 'application/json'
        }

        payload = json.dumps({
            "exchange": "NFO",
            "symboltoken": "57847",
            "interval": "ONE_MINUTE",
            "fromdate": from_time,
            "todate": to_time
        })

        conn.request("POST", "/rest/secure/angelbroking/historical/v1/getCandleData", payload, headers)
        res = conn.getresponse()
        data = res.read()
        parsed = json.loads(data.decode("utf-8"))

        if not parsed['status'] or not parsed.get('data'):
            logger.warning(f"No candle data received.")
            time.sleep(1)
            continue

        for candle in parsed['data']:
            timestamp   = candle[0]
            open_price  = candle[1]
            high_price  = candle[2]
            low_price   = candle[3]
            close_price = candle[4]
            volume      = candle[5]

            candle_time = datetime.fromisoformat(timestamp)  # timezone-aware

            # Check if this candle is finalized
            if candle_time < now.replace(second=0, microsecond=0):
                # Check for duplicate
                existing = supabase.table("live_data").select("timestamp").eq("timestamp", timestamp).execute()
                if not existing.data:
                    print(f"[INSERT] {timestamp} OHLC: {open_price}-{high_price}-{low_price}-{close_price} Vol:{volume}")
                    supabase.table("live_data").insert({
                        "timestamp": timestamp,
                        "open": open_price,
                        "high": high_price,
                        "low": low_price,
                        "close": close_price,
                        "ltp": close_price,
                        "volume": volume
                    }).execute()
            else:
                # Not finalized: send for live plotting (store temp file or pub/sub)
                with open("live_candle.json", "w") as f:
                    json.dump({
                        "timestamp": timestamp,
                        "open": open_price,
                        "high": high_price,
                        "low": low_price,
                        "close": close_price,
                        "volume": volume
                    }, f)

    except Exception as e:
        logger.error(f"Error: {e}")

    time.sleep(1)
