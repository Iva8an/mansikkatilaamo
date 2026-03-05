import unittest
import requests

class TestaaVarausKantaan(unittest.TestCase):
    """Perus testirakenne  http-yhteyksien testaamiseen."""
    def testaa_tiedon_syotto(self):
        payload = {
            "id": "123",
            "email": "test@mail",
            "maara": "1",
            "puh": "2",
            "pvm": "1"
        }

        vastaus = requests.post('http://localhost:8000/tilaus', json=payload)
        assert vastaus.status_code == 200 # add assertion here


if __name__ == '__main__':
    unittest.main()
