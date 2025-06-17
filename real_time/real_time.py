from SmartApi import SmartConnect
from dotenv import load_dotenv
from logzero import logger
from database_connection import supabase
import pyotp
import os
import json
import http.client
import time
from datetime import datetime

# Load API credentials
load_dotenv(dotenv_path="Your path to the .env file")

api_key = os.getenv("API_KEY")
CLIENT_CODE = os.getenv("CLIENT_CODE")
pwd = os.getenv("PASSWORD")
totp_secret = os.getenv("TOTP_SECRET")
local_ip = os.getenv("X-ClientLocalIP")
public_ip = os.getenv("X-ClientPublicIP")
mac_add = os.getenv("X-MACAddress")

# Create Smart API session
obj = SmartConnect(api_key)
session = obj.generateSession(CLIENT_CODE, pwd, pyotp.TOTP(totp_secret).now())

if not session['status']:
    logger.error(session)
    exit()

authToken = session['data']['jwtToken']
refreshToken = session['data']['refreshToken']
feedToken = obj.getfeedToken()
obj.generateToken(refreshToken)

while True:
    try:
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
            "symboltoken": "57847",  # Your symbol token
            "interval": "ONE_MINUTE",  # Use ONE_MINUTE, FIVE_MINUTE, etc.
            "fromdate": "2025-06-17 15:29",
            "todate": "2025-06-17 15:30"
        })

        conn.request("POST", "/rest/secure/angelbroking/historical/v1/getCandleData", payload, headers)
        res = conn.getresponse()
        data = res.read()
        parsed_data = json.loads(data.decode("utf-8"))

        print("RAW RESPONSE:", json.dumps(parsed_data, indent=2))

        # Safety check: ensure data exists and is not empty
        candle_data = parsed_data.get('data')
        if not candle_data or not isinstance(candle_data, list) or not candle_data[0]:
            raise ValueError("Candle data missing or malformed")

        # Extract candle info by index
        candle = candle_data[0]
        timestamp   = candle[0]
        open_price  = candle[1]
        high_price  = candle[2]
        low_price   = candle[3]
        close_price = candle[4]
        volume      = candle[5]

        print(f"[{timestamp}] Open: {open_price}, High: {high_price}, Low: {low_price}, Close: {close_price}, Volume: {volume}")

        # Insert into Supabase
        supabase.table("live_data").insert({
            "timestamp": timestamp,
            "open": open_price,
            "high": high_price,
            "low": low_price,
            "close": close_price,
            "ltp": close_price,  # Using close as LTP since real LTP is not returned
            "volume": volume
        }).execute()

    except Exception as e:
        logger.error(f"Error: {e}")

    time.sleep(1)  # polling interval
