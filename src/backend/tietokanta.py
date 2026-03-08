import os
from fastcrud import FastCRUD, crud_router
from dotenv import load_dotenv
from sqlite3 import Error
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy.sql.coercions import expect
from sqlmodel import Field, Session, SQLModel, create_engine, select
from schemas import TeeTilausSchema, PaivitaTilausSchema, PaivitaSaatavuusSchema, AnnaSaatavuusSchema
from models import Tilaus

# from src.frontend.tilaus import Tilaus


# Tässä lataan ympäristö muuttujia (mikäli niitä tarvitaan)
load_dotenv()

# Ensin teen SQLModel, typescript mallisesti tilaus hahmon,
# joka tulee olemaan pohja yhdelle tilaukselle
class TilausMalli(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(index=True)
    maara: int | None = Field(default=0, index=True)
    puh: str
    muuta: str
    pvm: str

class SaatavuusMalli(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    pvm: str
    laatikoden_maara: int | None = Field(default=0, index=True)
    hinta: int = Field(default=50)
    max: int = Field(default=50)

# Funktio, joka tarkistaa sqlite yhteyden kanta.db:hen, ja palauttaa onnistuneen yhteyden.
# Ei kuitenkaan ole toistaiseksi käytössä
"""def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
        print("Connection to SQLite DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection
"""
tilauskanta_nimi = "tilauskanta.db"
saatavuuskanta_nimi = "saatavuuskanta.db"
# sqlite:/// viittaa siihen, että kanta on olemassa vain sinä hetkenä, kun  ohjelma on käynnissä
saatavuuskanta_url = f"sqlite:///{saatavuuskanta_nimi}"
tilauskanta_url = f"sqlite:///{saatavuuskanta_nimi}"
# Tämän tarkoituksena on varmistaa että olisi vain yksi thread per. request
connect_args = {"check_same_thread": False}

# Luodaan tietokannan ajuri
engine1 = create_engine(tilauskanta_url, connect_args=connect_args)
engine2 = create_engine(saatavuuskanta_url, connect_args=connect_args)
# Luodaan kanta ja taulu:
def create_kannat():
    SQLModel.metadata.create_all(engine1)
    SQLModel.metadata.create_all(engine2)
# Luodaaan sessio, jotta engine eli ajuri pystyisi pysymään perässä muutoiksista
# jotka tulevat tietokantaan
def get_session1():
    with Session(engine1) as session:
        # yield pysättää funktion ja palauttaa arvon väliaikaisesti
        yield session

def get_session2():
    with Session(engine2) as session:
        yield session

# Tässä luodaan sessio, joka pitää olion muistissa ja pitää kirjaa muutoksista
SessionDep1 = Annotated[Session, Depends(get_session1)]
SessionDep2 = Annotated[Session, Depends(get_session2)]

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_kannat()
@app.post("/tilaus", tags=["Tilaus"])
def tee_tilaus(tilaus: TilausMalli, session: SessionDep1) -> TilausMalli:
    session.add(tilaus)
    session.commit()
    session.refresh(tilaus)
    return tilaus
@app.get("/saatavuus/{pvm}", tags=["Saatavuus"])
async def saatavuus_rajoitteet(pvm: str, session: SessionDep2) -> int:
    try:
        max = session.exec(select(SaatavuusMalli.max).where(SaatavuusMalli.pvm == pvm)).first()
        return max
    except Exception as e:
        return {"virhe": e}

"""@app.get("/maara", tags=["Tilaus"])  
def get_maxtilaus(pvm: str, session: SessionDep2) -> int:
    max_maara = session.exec(select(rajoitteet.max).where(rajoitteet.pvm == pvm)).first()
    if not max_maara:
        return 404
    return max_maara
"""