"""Quick notebook-friendly runner.

Run this file in a Jupyter cell with:
%run notebook_starter.py

It calls the FastAPI backend endpoints just like Streamlit does.
"""
import requests, json

API_URL = "http://localhost:8000"

payload = {
    "intent": "Announce Hack-Nation during Super Bowl season, highlight prizes, and invite teams to apply.",
    "event": "Super Bowl",
    "platform": "LinkedIn",
}

resp = requests.post(f"{API_URL}/generate", json=payload, timeout=300)
resp.raise_for_status()
data = resp.json()
print("Brand profile:")
print(json.dumps(data["brand_profile"], indent=2))
print("\nVariant 1:")
print(json.dumps(data["variants"][0], indent=2)[:1200], "...")
