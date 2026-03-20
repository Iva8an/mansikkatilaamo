import subprocess
import os
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Session, SQLModel, create_engine, select
from contextlib import asynccontextmanager
from models import TilausMalli, SaatavuusMalli
from sheets import suorita_sheet
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
tilauskanta_nimi = "tilauskanta.db"
saatavuuskanta_nimi = "saatavuuskanta.db"
# sqlite:/// viittaa siihen, että kanta on olemassa vain sinä hetkenä, kun  ohjelma on käynnissä
tilauskanta_url = f"sqlite:///{tilauskanta_nimi}"
saatavuuskanta_url = f"sqlite:///{saatavuuskanta_nimi}"
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

scheduler = AsyncIOScheduler()
steamlit_process = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global streamlit_process
    # Käynnistys
    create_kannat()
    streamlit_process = subprocess.Popen(
        ["streamlit", "run", os.path.join(BASE_DIR, "..", "frontend", "app.py"), "--server.port", "8501"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    suorita_sheet()
    scheduler.add_job(
        suorita_sheet,
        trigger=IntervalTrigger(hours=1),
        id="sheets_job",
        replace_existing=True
    )
    scheduler.start()
    yield
    # Sammutus - pysäytä Streamlit siististi
    if streamlit_process:
        streamlit_process.terminate()
        streamlit_process.wait()
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)

@app.post("/tilaus/", tags=["Tilaus"])
def tee_tilaus(tilaus: TilausMalli, session: SessionDep1) -> TilausMalli:
    session.add(tilaus)
    session.commit()
    session.refresh(tilaus)
    return tilaus
@app.get("/tilaus/{pvm}", tags=["Tilaus"])
def anna_tilaus(pvm: str, session: SessionDep1):
   try:
       with Session(engine1) as session:
           statement = select(TilausMalli).where(TilausMalli.pvm == pvm)
           results = session.exec(statement)
           tilaus = results.all()
           return tilaus
   except Exception as e:
       return {"virhe": e}

@app.get("/saatavuus/{pvm}", tags=["Saatavuus"])
async def saatavuus_rajoitteet(pvm: str, session: SessionDep2) -> list[int]:
    try:
        saatavuus = session.exec(select(SaatavuusMalli.laatikoidenMaara).where(SaatavuusMalli.pvm == pvm)).first()
        hinta = session.exec(select(SaatavuusMalli.hinta).where(SaatavuusMalli.pvm == pvm)).first()
        return [saatavuus, hinta]
    except Exception as e:
        return [0,0]

@app.post("/saatavuus/", tags=["Saatavuus"])
def lisaa_saatavuus(saatavuus: SaatavuusMalli, session: SessionDep2) -> SaatavuusMalli:
    session.add(saatavuus)
    session.commit()
    session.refresh(saatavuus)
    return saatavuus