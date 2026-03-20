from sqlmodel import Field, SQLModel


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
    laatikoidenMaara: int
    hinta: int
    max: int
