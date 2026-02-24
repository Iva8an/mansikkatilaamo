from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import DeclarativeBase



class Base(DeclarativeBase):
    pass

class Tilaus(Base):
    __tablename__ = 'tilaukset'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)