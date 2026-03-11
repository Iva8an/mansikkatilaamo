import gspread
from google.oauth2.service_account import Credentials
from translate import Translator
from datetime import datetime
import requests

scopes = [
    "https://www.googleapis.com/auth/spreadsheets"
]
creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
client = gspread.authorize(creds)
# Saatavuus-kannalle sheets
saatavuus_id = "1yQdxl4U8LaGJmmAncDeP7FgVRawBJd7ikgotX1Vr0eM"
# Tilaus-kannale sheets
tilaus_id = "1dzPS61cZY1aX_DAcOWmxmnd-zE9yhSQrNl8WKtlC1aA"

saatavuus_workbook = client.open_by_key(saatavuus_id)
tilaus_workbook = client.open_by_key(saatavuus_id)

tl = Translator(to_lang="fi")
month = datetime.now().strftime("%B")
tama_kuu = tl.translate(month)
tanaan = datetime.today().strftime("%Y-%m-%d")


uusi_saatavuussheet_nimi = f"{tama_kuu}"
saatavuus_sheet_lista = map(lambda x: x.title, saatavuus_workbook.worksheets())

uusi_tilaussheet_nimi = f"{tama_kuu}"
tilaus_sheet_lista = map(lambda x: x.title, tilaus_workbook.worksheets())

#Tarkistetaanko onko sheets-taulu jo olemassa
if uusi_saatavuussheet_nimi in saatavuus_sheet_lista:
    saatavuus_sheet = saatavuus_workbook.worksheet(f"{tama_kuu}")
else:
    saatavuus_sheet = saatavuus_workbook.add_worksheet(f"{tama_kuu}", rows=31, cols=1)

if uusi_tilaussheet_nimi in tilaus_sheet_lista:
    tilaus_sheet = saatavuus_workbook.worksheet(f"{tama_kuu}")
else:
    tilaus_sheet = saatavuus_workbook.add_worksheet(f"{tama_kuu}", rows=31, cols=1)

requests.get("http://localhost/tilaus")