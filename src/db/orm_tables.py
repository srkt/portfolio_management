from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import sys

sys.path.append("")
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


class StockTechnicalAnalysis(Base):
    __tablename__ = cf.STOCK_TECHNICAL_ANALYSIS

    Id = Column(Integer, primary_key=True)
    Ticker = Column(String)
    Date = Column(String)
    Close = Column(Float)
    Volume = Column(Integer)
    SMA5 = Column(Float)
    SMA10 = Column(Float)
    SMA21 = Column(Float)
    SMA50 = Column(Float)
    SMA100 = Column(Float)
    SMA200 = Column(Float)


class Tickers(Base):
    __tablename__ = cf.TABLE_TICKERS

    Ticker = Column(String, primary_key=True)
    Sector = Column(String)
    Industry = Column(String)
    Include_In_Analysis = Column(String)
    Last_Update_Date = Column(String)
    Last_Er_Date = Column(String)
    Er_Rating = Column(String)
    Er_Beat = Column(String)
    AVWAP_1 = Column(String)
    AVWAP_2 = Column(String)
    AVWAP_3 = Column(String)
    AVWAP_4 = Column(String)
    AVWAP_5 = Column(String)


class TickerLog(Base):
    __tablename__ = cf.TICKER_LOG

    Ticker = Column(String, primary_key=True)
    Last_Updated_On = Column(String)


class Config(Base):
    __tablename__ = cf.CONFIG

    Id = Column(Integer, primary_key=True)
    Last_Refresh_Date = Column(String)


class MultiVwapPoints(Base):
    __tablename__ = cf.MULTI_AVWAP_POINTS

    Id = Column(Integer, primary_key=True)
    Ticker = Column(String)
    Anchor_Date = Column(String)
    Notes = Column(String)


class AVwapData(Base):
    __tablename__ = cf.AVWAP_DATA

    Id = Column(Integer, primary_key=True)
    Point_Id = Column(String)
    Close = Column(Float)
    Avwap = Column(Float)
