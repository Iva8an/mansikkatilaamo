import gspread
import requests
import random
from google.oauth2.service_account import Credentials
from translate import Translator
from datetime import datetime

def alustus() -> dict:
    alustettu = {}
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
    alustettu.update({"Tanaan"  : datetime.today().strftime("%Y-%m-%d")})


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
        tilaus_sheet = tilaus_workbook.worksheet(f"{tama_kuu}")
    else:
        tilaus_sheet = tilaus_workbook.add_worksheet(f"{tama_kuu}", rows=31, cols=1)

    alustettu.update({"Saatavuus-sheet": saatavuus_sheet})
    alustettu.update({"Tilaus-sheet": tilaus_sheet})
    return alustettu

def suorita_saatavuus():
    alustettu = alustus()
    saatavuus_sheet = alustettu["Saatavuus-sheet"]
    tilaus_sheet = alustettu["Tilaus-sheet"]
    tanaan = alustettu["Tanaan"]

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

    saatavuus_tanaan = [{
        "id": random.randrange(1000000,10000000000),
        "pvm" : f"{paivamaara_tanaan}",
        "laatikoiden_maara" : laatikot_tanaan,
        "laatikoidenMaara" : int(laatikot_tanaan),
        "hinta": hinta_tanaan,
        "max": max_tanaan
    }]

    requests.post("http://localhost:8000/saatavuus/", json=saatavuus_tanaan)

def suorita_tilaus():
    alustettu = alustus()
    saatavuus_sheet = alustettu["Saatavuus-sheet"]
    tilaus_sheet = alustettu["Tilaus-sheet"]
    tanaan = alustettu["Tanaan"]
    uudet_tilaukset = requests.get(f"http://localhost:8000/tilaus/{tanaan}")
    tilaukset = uudet_tilaukset.json()[0]
    for tilaus in tilaukset:
        sheet_tilaus = [
            [
                tilaus.get("id"),
                tilaus.get("email"),
                tilaus.get("maara"),
                tilaus.get("puh"),
                tilaus.get("muuta"),
                tilaus.get("pvm"),
             ]
        ]
        tilaus_sheet.update(f"A2:G{len(tilaukset)}", sheet_tilaus)

_alustettu = False
def suorita_sheet():
    global _alustettu
    if not _alustettu:
        alustus()
        _alustettu = True
    suorita_saatavuus()
    suorita_tilaus()
