from supabase import create_client, Client
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path="Path to the database.env")

project_url = os.getenv("supabaseUrl")
project_key = os.getenv("supabase_key")

#Url and API parsing.
url: str = project_url
key: str = project_key

#Creating client session.
supabase : Client = create_client(url,key)

# print(supabase.table("live_data").select("*").limit(1).execute().data)