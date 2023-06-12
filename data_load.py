from sqlalchemy import create_engine
import config as cf
from portfolio_optimization import Portfolio
import tables
from sqlalchemy import create_engine, func, Date
from sqlalchemy.orm import sessionmaker
import config as cf
import pandas as pd
import pandas_datareader as pdr
import yfinance as yf
import csv

# Define the database connection
engine = create_engine(cf.DB_CONNECTION)
Session = sessionmaker(bind=engine)
session = Session()


def get_stocks_data(ticker, start, end):
    yf.pdr_override()
    stocks_data = pdr.get_data_yahoo(ticker, start, end)
    stocks_data.insert(0, "Ticker", ticker)
    db_engine = create_engine(
        cf.DB_CONNECTION,
        echo=False,
    )
    stocks_data.to_sql("stock_data", con=db_engine, if_exists="append")


#
def load_symbols_into_db():
    with open("symbols.csv", newline="") as csvfile:
        symbol_reader = csv.reader(csvfile, delimiter=",", quotechar="|")
        # skip header
        next(symbol_reader)
        for row in symbol_reader:
            print("loading " + row[0] + "...")
            get_stocks_data(row[0], "2013-01-01", "2023-06-09")


def get_ticker_data(ticker):
    condition = tables.StockData.Ticker == ticker

    query = session.query(
        tables.StockData.Adj_Close.label(ticker),
        func.date(tables.StockData.Date).label("Date"),
    ).filter(condition)

    result = session.execute(query)

    df = pd.DataFrame(result.fetchall(), columns=[ticker, "Date"])
    df.set_index("Date", inplace=True)
    return df


def get_tickers():
    query = session.query(tables.Tickers.Ticker)
    result = session.execute(query)
    return [r for r, in result.fetchall()]
