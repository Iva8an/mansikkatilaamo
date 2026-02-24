from pydantic import BaseModel

# Tämä luokka on vastuussa scheemoista, joita tilaustietokannassa voidaan toteuttaa.
class TeeTilausSchema(BaseModel):
    name: str
    description: str

class PaivitaTilausSchema(BaseModel):
    pass