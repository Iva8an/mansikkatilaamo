import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool  

from src.backend.tietokanta import app, get_session1

@pytest.fixture(name="session")  
def session_fixture():  
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session 

def test_tee_tilaus(session: Session):
    def get_session_override():
        return session
    
    app.dependency_overrides[get_session1] = get_session_override

    client = TestClient(app)

    response = client.post(
        "/tilaus/", json={"id": 123, "email": "moikku@gmail.fi", "maara": 2, "puh": "05042314", "muuta": "blabla", "pvm": "2026-09-09"}
    )
    app.dependency_overrides.clear()
    data = response.json()

    assert response.status_code == 200
    assert data["id"] == 123
    assert data["email"] == "moikku@gmail.fi"
    assert data["maara"] == 2
    assert data["puh"] == "05042314"
    assert data["muuta"] == "blabla"
    assert data["pvm"] == "2026-09-09"
