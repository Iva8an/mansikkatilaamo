import pytest
import requests
from google.oauth2.service_account import Credentials
from src.backend.sheets import saatavuus_id, tilaus_id, tilaus_sheet, saatavuus_sheet

 
def testaa_saatavuus_sheet_yhteys():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets"
    ]
    creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
    headers = {'authorization': f'Bearer {creds}','Content-Type': 'application/vnd.api+json'}
    saatavuus_url = f'https://sheets.googleapis.com/v4/spreadsheets/{saatavuus_id}/values/{saatavuus_sheet}'
    response = requests.get(saatavuus_url, headers=headers)
    assert response.status_code == 200
    