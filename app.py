from flask import Flask, request
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
import re

app = Flask(__name__)

# Define the scope for Google Sheets and Drive API
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Load credentials from environment variable
google_creds = json.loads(os.environ["GOOGLE_CREDENTIALS"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(google_creds, scope)

# Authorize the client
client = gspread.authorize(creds)

# Open the spreadsheet
spreadsheet = client.open("Ausentismo Iscot").sheet1

# Function to extract data from message text
def extract_fields(message):
    patterns = {
        "nombre": r"(?i)nombre\s*[:\-]\s*(.+)",
        "servicio": r"(?i)servicio\s*[:\-]\s*(.+)",
        "legajo": r"(?i)legajo\s*[:\-]\s*(\d+)",
        "motivo": r"(?i)motivo\s*[:\-]\s*(.+)",
        "dias": r"(?i)d[ií]as\s*[:\-]\s*(\d+)"
    }
    extracted = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, message)
        extracted[key] = match.group(1).strip() if match else ""
    return extracted

# Webhook endpoint
@app.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.values.get("Body", "").strip()
    fields = extract_fields(incoming_msg)

    # Append data to Google Sheet
    spreadsheet.append_row([
        fields["nombre"],
        fields["servicio"],
        fields["legajo"],
        fields["motivo"],
        fields["dias"]
    ])

    return "Datos recibidos y registrados correctamente", 200

# Run the Flask app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)


