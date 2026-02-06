import datetime

class Tilaus:
    
    def Valitse_nouto_pvm() -> datetime:
        """Palauttaa pvm kalenterista"""

    def Kuinkapaljon_mita() -> tuple:
        """Kuinka paljon laatikoita tulee tilaukseen
        jota sitten palautetaan tuplena backendiin"""
    
    def Yhteystiedot() -> dict:
        """Palauttaa sanakirjan eli hashtablen yhteystiedoista, joka
        sitten välitetään tietokantaan"""

    def Ekstrainfo() -> str:
        """HelloWorld vaiheen viesti"""
        """Asiakas pystyy antamaan lisätietoa hänen tilauksestaan"""

    def AnnaHinta() -> int:
        """Kokonaisluku, joka tulee olemaan tulo Kuinkapaljon_mita() funktiosta ja 
        hinta per kappaleesta"""
    