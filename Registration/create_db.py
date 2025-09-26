# db.py
import os
from supabase import create_client, Client
from dotenv import load_dotenv
load_dotenv()

# ✅ Your Supabase credentials (keep these secret in production)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
# ✅ Create Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ✅ Insert new user into Supabase
def insert_user(username: str, password_hash: str, department: str):
    response = supabase.table("users").insert({
        "username": username,
        "password": password_hash,
        "department": department
    }).execute()

    # ✅ Only raise if error exists and insert failed
    if hasattr(response, "error") and response.error:
        raise Exception(f"Insert failed: {response.error.message}")

    if not response.data:
        raise Exception("Insert failed: No data returned.")

    return response.data[0]  # Return inserted user

# ✅ Fetch user by username
def get_user_by_username(username: str):
    response = supabase.table("users").select("*").eq("username", username).execute()

    if hasattr(response, "error") and response.error:
        raise Exception(f"Fetch failed: {response.error.message}")

    if not response.data:
        return None

    return response.data[0]
