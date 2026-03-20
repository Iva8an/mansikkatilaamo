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

def suorita_saatavuus(alustettu):
    saatavuus_sheet = alustettu["Saatavuus-sheet"]
    tilaus_sheet = alustettu["Tilaus-sheet"]
    tanaan = alustettu["Tanaan"]

    rivit = saatavuus_sheet.get_all_records()
    saatavuus_lista = []
    for rivi in rivit:
        if rivi["päivämäärä"] >= tanaan:  # muuta "pvm" sheetin otsikon mukaan
            saatavuus_lista.append({
                "id": random.randrange(1000000, 10000000000),
                "pvm": rivi["päivämäärä"],
                "laatikoidenMaara": int(rivi["laatikoiden määrä"]),
                "hinta": int(rivi["kappale hinta"]),
                "max": int(rivi["max"])
            })

    requests.post("http://localhost:8000/saatavuus/", json=saatavuus_lista)

def suorita_tilaus(alustettu):
    saatavuus_sheet = alustettu["Saatavuus-sheet"]
    tilaus_sheet = alustettu["Tilaus-sheet"]
    tanaan = alustettu["Tanaan"]
    response = requests.get("http://localhost:8000/tilaus/synkronoimattomat")
    tilaukset = response.json()

    for tilaus in tilaukset:
        tilaus_sheet.append_row([
            tilaus["id"],
            tilaus["email"],
            tilaus["maara"],
            tilaus["puh"],
            tilaus["muuta"],
            tilaus["pvm"]
        ])

    # Merkitse synkronoiduiksi
    requests.post("http://localhost:8000/tilaus/merkitse-synkronoiduksi",json=[t["id"] for t in tilaukset])

_alustettu = None
def suorita_sheet():
    global _alustettu
    if not _alustettu:
        _alustettu = alustus()

    suorita_saatavuus(_alustettu)
    suorita_tilaus(_alustettu)