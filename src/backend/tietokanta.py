import os
from fastcrud import FastCRUD, crud_router
from dotenv import load_dotenv
from sqlite3 import Error
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select
from schemas import TeeTilausSchema, PaivitaTilausSchema, PaivitaSaatavuusSchema
from models import Tilaus
from src.backend.schemas import AnnaSaatavuusSchema

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
    pvm: str

class SaatavuusMalli(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    pvm: str
    maara: int | None = Field(default=0, index=True)

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

tilaus_router = crud_router(
    session=get_session1,
    model=TilausMalli,
    create_schema=TeeTilausSchema,
    update_schema=PaivitaTilausSchema,
    path="/tilaus",
    tags=["Tilaus"]
)
saatavuus_router = crud_router(
    session=get_session2,
    model=SaatavuusMalli,
    create_schema=AnnaSaatavuusSchema,
    update_schema=PaivitaSaatavuusSchema,
    path="/saatavuus",
    tags=["Saatavuus"]
)
@app.post("/tilaus", tags=["Tilaus"])
def tee_tilaus(tilaus: TilausMalli, session: SessionDep1) -> TilausMalli:
    session.add(tilaus)
    session.commit()
    session.refresh(tilaus)
    return tilaus

@app.get("/saatavuus", tags=["Saatavuus"])
def get_saatavuus(saatavuus: SaatavuusMalli, session: SessionDep2) -> SaatavuusMalli:
    session.add(saatavuus)
    session.commit()
    session.refresh(saatavuus)
    return saatavuus