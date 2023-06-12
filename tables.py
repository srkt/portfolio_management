from sqlalchemy import create_engine, Column, Integer, String, Numeric, Date, Float
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import config as cf

# Define the database connection
engine = create_engine(cf.DB_CONNECTION)
Session = sessionmaker(bind=engine)
session = Session()

# Define the declarative base
Base = declarative_base()


# Define the table model
class StockData(Base):
    __tablename__ = cf.TABLE_STOCK_DATA

    Id = Column(Integer, primary_key=True)
    Ticker = Column(String)
    Date = Column(String)
    Open = Column(Float)
    High = Column(Float)
    Low = Column(Float)
    Close = Column(Float)
    Adj_Close = Column("Adj Close", Float)
    Volume = Column(Integer)


class Tickers(Base):
    __tablename__ = cf.TABLE_TICKERS

    Ticker = Column(String, primary_key=True)
    Sector = Column(String)
    Industry = Column(String)
    Include_In_Analysis = Column(String)
