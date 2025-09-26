import os
from msal import PublicClientApplication, SerializableTokenCache
from dotenv import load_dotenv
load_dotenv()

CLIENT_ID = os.getenv("Client_ID") 
TENANT_ID = "common"  # Use your org tenant in production
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPES = ["Files.ReadWrite.All", "User.Read"]
CACHE_FILE = "token_cache.json"

def get_token():
    # Load or create a token cache
    token_cache = SerializableTokenCache()
    if os.path.exists(CACHE_FILE):
        token_cache.deserialize(open(CACHE_FILE, "r").read())

    app = PublicClientApplication(
        CLIENT_ID,
        authority=AUTHORITY,
        token_cache=token_cache,
    )

    # Try silent login using cache
    accounts = app.get_accounts()
    if accounts:
        result = app.acquire_token_silent(SCOPES, account=accounts[0])
    else:
        result = app.acquire_token_interactive(SCOPES)

    # Save cache
    if token_cache.has_state_changed:
        with open(CACHE_FILE, "w") as f:
            f.write(token_cache.serialize())

    if "access_token" in result:
        return result["access_token"]
    raise Exception("Failed to get access token")
