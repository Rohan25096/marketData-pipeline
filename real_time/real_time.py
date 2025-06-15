from SmartApi import SmartConnect #or from SmartApi.smartConnect import SmartConnect
from dotenv import load_dotenv
import pyotp
import os
from logzero import logger

load_dotenv(dotenv_path="Your path to the .env file.")

api_key = os.getenv("API_KEY")
CLIENT_CODE = os.getenv("CLIENT_CODE")
pwd = os.getenv("PASSWORD")
totp_secret = os.getenv("TOTP_SECRET")
local_ip = os.getenv("X-ClientLocalIP")
public_ip = os.getenv("X-ClientPublicIP")
mac_add = os.getenv("X-MACAddress")

obj = SmartConnect(api_key)

correlation_id = "Live_data"
session = obj.generateSession(CLIENT_CODE, pwd, pyotp.TOTP(totp_secret).now())

if session['status'] == False:
    logger.error(session)
    
else:
    # fetch the feedtoken
    feedToken = obj.getfeedToken()

    authToken = session['data']['jwtToken']
    refreshToken = session['data']['refreshToken']
    print(authToken)

    # fetch User Profile
    res = obj.getProfile(refreshToken)
    obj.generateToken(refreshToken)
    res=res['data']['exchanges']



import http.client
import json

conn = http.client.HTTPSConnection("apiconnect.angelone.in")
payload = {
    "mode": "FULL",
    "exchangeTokens": {
        "NSE": ["2263"]
    }
}
headers = {
  'X-PrivateKey': api_key,
  'Accept': 'application/json',
  'X-SourceID': 'WEB',
  'X-ClientLocalIP': local_ip,
  'X-ClientPublicIP': public_ip,
  'X-MACAddress': mac_add,
  'X-UserType': 'USER',
  'Authorization': authToken,
  'Accept': 'application/json',
  'X-SourceID': 'WEB',
  'Content-Type': 'application/json'
}
conn.request("POST", "/rest/secure/angelbroking/market/v1/quote/", json.dumps(payload), headers)
res = conn.getresponse()
data = res.read()
DATA = data.decode("utf-8")
parsed_data = json.loads(DATA)

#Extracting stock info from response.
stock_info = parsed_data['data']['fetched'][0]

open_price = stock_info['open']
high_price = stock_info['high']
low_price = stock_info['low']
close_price = stock_info['close']
volume = stock_info['tradeVolume']
ltp = stock_info['ltp']
