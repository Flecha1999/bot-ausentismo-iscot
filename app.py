from flask import Flask, request
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import re

app = Flask(__name__)

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("google_credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("Ausentismo Iscot").sheet1

# Function to extract data from message
def extract_data(message):
    # Regular expressions to extract fields
    nombre_match = re.search(r"(?i)nombre\s*[:\-]?\s*(.+)", message)
    servicio_match = re.search(r"(?i)servicio\s*[:\-]?\s*(.+)", message)
    legajo_match = re.search(r"(?i)legajo\s*[:\-]?\s*(\d+)", message)
    motivo_match = re.search(r"(?i)motivo\s*[:\-]?\s*(.+)", message)
    dias_match = re.search(r"(?i)d[ií]as\s*[:\-]?\s*(\d+)", message)

    nombre = nombre_match.group(1).strip() if nombre_match else ""
    servicio = servicio_match.group(1).strip() if servicio_match else ""
    legajo = legajo_match.group(1).strip() if legajo_match else ""
    motivo = motivo_match.group(1).strip() if motivo_match else ""
    dias = dias_match.group(1).strip() if dias_match else ""

    return nombre, servicio, legajo, motivo, dias

@app.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.values.get("Body", "").strip()
    nombre, servicio, legajo, motivo, dias = extract_data(incoming_msg)

    # Save to Google Sheets
    sheet.append_row([nombre, servicio, legajo, motivo, dias])

    return "Datos registrados correctamente", 200

if __name__ == "__main__":
    app.run(debug=True)

