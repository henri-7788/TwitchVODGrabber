# twitch_diag.py
import os, requests
from pathlib import Path
from dotenv import load_dotenv

# .env laden (auch wenn das Script aus einem anderen Pfad gestartet wird)
load_dotenv(dotenv_path=Path(__file__).with_name(".env"))

# Variablen lesen (mit Fallbacks)
CLIENT_ID = os.getenv("TWITCH_CLIENT_ID") or os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("TWITCH_ACCESS_TOKEN") or os.getenv("CLIENT_SECRET")

def ok(v): return v and len(v) > 6

print("ENV check:")
print("  TWITCH_CLIENT_ID:", (CLIENT_ID[:3] + "..." + CLIENT_ID[-3:]) if ok(CLIENT_ID) else "NICHT GESETZT")
print("  TWITCH_CLIENT_SECRET:", ("***" + CLIENT_SECRET[-4:]) if ok(CLIENT_SECRET) else "NICHT GESETZT")

assert ok(CLIENT_ID) and ok(CLIENT_SECRET), "Client-ID/-Secret fehlen oder falsche Variablennamen in .env"

def get_app_access_token():
    r = requests.post(
        "https://id.twitch.tv/oauth2/token",
        data={"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET, "grant_type": "client_credentials"},
        timeout=20,
    )
    print("Token endpoint:", r.status_code)
    if r.status_code != 200:
        print("Antwort:", r.text)
    r.raise_for_status()
    return r.json()["access_token"]

token = get_app_access_token()
print("Token geholt (len):", len(token))

headers = {"Client-ID": CLIENT_ID, "Authorization": f"Bearer {token}"}
r = requests.get("https://api.twitch.tv/helix/users", params={"login": "sb737"}, headers=headers, timeout=20)
print("Helix /users Status:", r.status_code)
print("Body:", r.text[:300])
