import subprocess
import os
from datetime import datetime, timedelta
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Session, SQLModel, create_engine, select
from contextlib import asynccontextmanager
from models import TilausMalli, SaatavuusMalli
from sheets import suorita_sheet
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from typing import List

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
    scheduler.add_job(
        suorita_sheet,
        trigger=IntervalTrigger(hours=1),
        id="sheets_job",
        replace_existing=True,
        next_run_time=datetime.now() + timedelta(seconds=5),
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
        statement = select(TilausMalli).where(TilausMalli.pvm == pvm)
        results = session.exec(statement)
        tilaus = results.all()
        return tilaus
   except Exception as e:
       return {"virhe": e}

@app.get("/tilaus/synkronoimattomat", tags=["Tilaus"])
def anna_synkronoimattomat(session: SessionDep1):
    statement = select(TilausMalli).where(TilausMalli.synkronoitu == False)
    return session.exec(statement).all()

@app.post("/tilaus/merkitse-synkronoiduksi", tags=["Tilaus"])
def merkitse_synkronoiduksi(ids: List[int], session: SessionDep1):
    for id in ids:
        tilaus = session.get(TilausMalli, id)
        if tilaus:
            tilaus.synkronoitu = True
    session.commit()
    return {"merkitty": len(ids)}

@app.get("/saatavuus/{pvm}", tags=["Saatavuus"])
async def saatavuus_rajoitteet(pvm: str, session: SessionDep2) -> list[int]:
    try:
        saatavuus = session.exec(select(SaatavuusMalli.laatikoidenMaara).where(SaatavuusMalli.pvm == pvm)).first()
        hinta = session.exec(select(SaatavuusMalli.hinta).where(SaatavuusMalli.pvm == pvm)).first()
        return [saatavuus, hinta]
    except Exception as e:
        return [0,0]

@app.post("/saatavuus/", tags=["Saatavuus"])
def lisaa_saatavuus(saatavuudet: List[SaatavuusMalli], session: SessionDep2) -> List[SaatavuusMalli]:
    for saatavuus in saatavuudet:
        session.add(saatavuus)
    session.commit()
    for saatavuus in saatavuudet:
        session.refresh(saatavuus)
    return saatavuudet