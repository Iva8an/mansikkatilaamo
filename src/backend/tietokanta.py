import os
import sqlite3
from dotenv import load_dotenv
from sqlite3 import Error
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Query
from packaging.metadata import Metadata
from sqlmodel import Field, Session, SQLModel, create_engine, select
from src.frontend.tilaus import Tilaus
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
kanta_nimi = "kanta.db"
# sqlite:/// viittaa siihen, että kanta on olemassa vain sinä hetkenä, kun  ohjelma on käynnissä
kanta_url = f"sqlite:///{kanta_nimi}"

# Tämän tarkoituksena on varmistaa että olisi vain yksi thread per. request
connect_args = {"check_same_thread": False}

# Luodaan tietokannan ajuri
engine = create_engine(kanta_url, connect_args=connect_args)

# Luodaan kanta ja taulu:
def create_kanta():
    SQLModel.metadata.create_all(engine)

# Luodaaan sessio, jotta engine eli ajuri pystyisi pysymään perässä muutoiksista
# jotka tulevat tietokantaan
def get_session():
    with Session(engine) as session:
        # yield pysättää funktion ja palauttaa arvon väliaikaisesti
        yield session

# Tässä luodaan sessio, joka pitää olion muistissa ja pitää kirjaa muutoksista
SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_kanta()



