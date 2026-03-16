import unittest
import requests

"""class TestaaVarausKantaan(unittest.TestCase):
    #Perus testirakenne  http-yhteyksien testaamiseen.
    def testaa_tiedon_syotto(self):
        payload = {
            "id": 10,
            "email": "test@mail",
            "maara": 1,
            "puh": "2",
            "muuta" : "jtn",
            "pvm": "1"
        }

        vastaus = requests.post('http://localhost:8000/tilaus/', json=payload)
        assert vastaus.status_code == 200 # add assertion here"""
"""
class TestaaSaatavuus(unittest.TestCase):
    
    def testaa_tiedon_saanti(self):
        testi_pvm = "2026-03-10"
        vastaus = requests.get(f'http://localhost:8000/saatavuus/{testi_pvm}')
        assert vastaus.status_code == 200 # add assert here


class TestaaEpaonnistuminen(unittest.TestCase):

    def testaa_epaonnistunut_saanti(self):
            testi_pvm = "2026-03-11"
            vastaus = requests.get(f'http://localhost:8000/saatavuus/{testi_pvm}')
            assert vastaus.status_code == 500 # add assert here

class TestaaEpaonnistunutTilaus(unittest.TestCase):
     
     def testaa_epaonnistunut_tilaus(self):
            testi_pvm = "2026-03-11"
            vastaus = requests.get(f'http://localhost:8000/saatavuus/{testi_pvm}')
            assert vastaus.status_code == 500 # add assert here

class TestaaMockSaatavuus(unittest.TestCase):
     
     def testaa_palautuuko_arvot(self):
          """"""


"""