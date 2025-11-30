import time, datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import os

# Load JSON key from Render Secret
json_key = os.getenv("GOOGLE_SERVICE_ACCOUNT")
creds_dict = json.loads(json_key)

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
gc = gspread.authorize(creds)

USERS_SHEET_ID = "1D6MJDeSbzDwHJ968ov01RniHwXnpfhSzDAnSJsi3_PE"
LICENSE_SHEET_ID = "1eibI7GihwhOKxpuHlA2SOR_yEiiPiAJ-0VwW9ITn9so"

def read_users():
    ws = gc.open_by_key(USERS_SHEET_ID).sheet1
    return [r["username"] for r in ws.get_all_records()]

def read_licenses():
    ws = gc.open_by_key(LICENSE_SHEET_ID).sheet1
    rows = ws.get_all_records()
    today = datetime.date.today()

    allowed = []
    for r in rows:
        username = r["username"]
        exp = r["expires_at"].lower()
        active = r["active"].upper() in ["TRUE", "YES", "1"]

        if not username or not active:
            continue

        if exp == "lifetime":
            allowed.append(username)
            continue

        exp_date = datetime.datetime.strptime(exp, "%Y-%m-%d").date()
        if exp_date >= today:
            allowed.append(username)

    return allowed

def compute_signal():
    t = int(time.time())
    return "BUY" if (t // 20) % 2 == 0 else "SELL"

print("=== Render Server Started ===")

while True:
    try:
        users = read_users()
        licenses = read_licenses()
        allowed = [u for u in users if u in licenses]
        signal = compute_signal()
        timestamp = datetime.datetime.utcnow().isoformat()

        print(f"[{timestamp}] Allowed users: {allowed}")
        print(f"[{timestamp}] Signal: {signal}")
        print(f"[{timestamp}] (demo) Would send to: {allowed}")

    except Exception as e:
        print("Error:", e)

    time.sleep(10)
