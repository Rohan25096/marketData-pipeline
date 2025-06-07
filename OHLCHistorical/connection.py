from SmartApi.smartConnect import SmartConnect
from dotenv import load_dotenv
import os
import pandas as pd
import requests
import pyotp

load_dotenv()

api_key = os.getenv("API_KEY")
pwd = os.getenv("PASSWORD")
CLIENT_CODE = os.getenv("CLIENT_CODE")
totp_secret = os.getenv("TOTP_SECRET")

obj = SmartConnect(api_key)
session = obj.generateSession(CLIENT_CODE,pwd,pyotp.TOTP(totp_secret).now())
feed_token = obj.getfeedToken
auth_token = session['data']['jwtToken']
refresh_token = session['data']['refreshToken']