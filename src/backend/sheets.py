import gspread
from google.oauth2.service_account import Credentials
from translate import Translator
from datetime import datetime
import random
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
tilaus_workbook = client.open_by_key(tilaus_id)

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
    saatavuus_sheet = saatavuus_workbook.add_worksheet(f"{tama_kuu}", rows=31, cols=4)

if uusi_tilaussheet_nimi in tilaus_sheet_lista:
    tilaus_sheet = saatavuus_workbook.worksheet(f"{tama_kuu}")
else:
    tilaus_sheet = saatavuus_workbook.add_worksheet(f"{tama_kuu}", rows=100000000, cols=7)


paivamaarat = saatavuus_sheet.col_values(1)
paivamaara_cells = {}
laatikot_cells = {}
hinta_cells = {}
max_cells = {}
for i in range(1, len(paivamaarat)):
    paivamaara_cells.update({paivamaarat[i] : f"A{i+1}"})
    laatikot_cells.update({paivamaarat[i]: f"B{i+1}"})
    hinta_cells.update({paivamaarat[i]: f"C{i+1}"})
    max_cells.update({paivamaarat[i]: f"D{i+1}"})
paivamaara_tanaan = saatavuus_sheet.acell(f"{paivamaara_cells.get(tanaan)}").value
laatikot_tanaan = saatavuus_sheet.acell(f"{laatikot_cells.get(tanaan)}").value
hinta_tanaan = saatavuus_sheet.acell(f"{hinta_cells.get(tanaan)}").value
max_tanaan = saatavuus_sheet.acell(f"{max_cells.get(tanaan)}").value

saatavuus_tanaan = {
    "id": random.randrange(1000000,10000000000),
    "pvm" : f"{paivamaara_tanaan}",
    "laatikoidenMaara" : int(laatikot_tanaan),
    "hinta": hinta_tanaan,
    "max": max_tanaan
}
print(list(tilaus_sheet_lista))
print(tama_kuu)
requests.post("http://localhost:8000/saatavuus/", json=saatavuus_tanaan)

uudet_tilaukset = requests.get(f"http://localhost:8000/tilaus/{tanaan}")
print(uudet_tilaukset.json())
tilaus = [
    [
        uudet_tilaukset.json()[0].get("id"),
        uudet_tilaukset.json()[0].get("email"),
        uudet_tilaukset.json()[0].get("maara"),
        uudet_tilaukset.json()[0].get("puh"),
        uudet_tilaukset.json()[0].get("muuta"),
        uudet_tilaukset.json()[0].get("pvm"),
     ]
]
print(tilaus)
tilaus_sheet.update(f"A2:G2", tilaus)
