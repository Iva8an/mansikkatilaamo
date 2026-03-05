from pydantic import BaseModel

# Tämä luokka on vastuussa scheemoista, joita tilaustietokannassa voidaan toteuttaa.
class TeeTilausSchema(BaseModel):
    pass

class PaivitaTilausSchema(BaseModel):
    pass

class AnnaSaatavuusSchema(BaseModel):
    pass

class PaivitaSaatavuusSchema(BaseModel):
    pass