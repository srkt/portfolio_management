import sys
from sqlalchemy import create_engine, func, Date
from sqlalchemy.orm import sessionmaker
import pandas as pd
import pandas_datareader as pdr
import yfinance as yf
import csv
import src.db.orm_tables as tables


sys.path.append("")
import config as cf


# Define the database connection
engine = create_engine(cf.DB_CONNECTION)
Session = sessionmaker(bind=engine)
session = Session()


# Loads stock data for a given ticker from yfinance into database
def load_stock_data_into_db(ticker, start, end):
    yf.pdr_override()
    stocks_data = pdr.get_data_yahoo(ticker, start, end)
    stocks_data.insert(0, "Ticker", ticker)
    db_engine = create_engine(
        cf.DB_CONNECTION,
        echo=False,
    )
    stocks_data.to_sql("stock_data", con=db_engine, if_exists="append")


# Retrives all tickers in database
def get_all_tickers_in_db():
    query = session.query(tables.Tickers.Ticker)
    result = session.execute(query)
    return [r for r, in result.fetchall()]


# Returns list of tickers from textfile at file path (only single column with tickers)
def get_tickers_from_file(file_path):
    data = []

    with open(file_path, "r") as file:
        reader = csv.reader(file)
        for row in reader:
            data.append(row[0])

    return data


# Loads stock data for given ticker list between given start and finish dates
def load_multiple_stock_data_into_db(
    ticker_list,
    start_date="2013-01-01",
    end_date="2023-06-09",
):
    for ticker in ticker_list:
        print("loading " + ticker + "...")
        load_stock_data_into_db(ticker, start_date, end_date)


# Loads stock data into database for tickers in given file between start and finish dates
def load_stock_data_into_db(
    file_path="../../symbols.csv",
    start_date="2013-01-01",
    end_date="2023-06-09",
):
    with open(file_path, newline="") as ticker_file:
        symbol_reader = csv.reader(ticker_file, delimiter=",", quotechar="|")
        for row in symbol_reader:
            print("loading " + row[0] + "...")
            load_stock_data_into_db(row[0], start_date, end_date)


# Returns pandas stock dataframe stored in database for given ticker
def get_stock_dataframe(ticker, start_date=None, finish_date=None):
    condition = tables.StockData.Ticker == ticker

    query = session.query(
        tables.StockData.Adj_Close.label(ticker),
        func.date(tables.StockData.Date).label("Date"),
    ).filter(condition)

    result = session.execute(query)
    df = pd.DataFrame(result.fetchall(), columns=[ticker, "Date"])
    df.set_index("Date", inplace=True)
    return df


# Returns adjusted close dataframe for given tickers
def get_adj_close_dataframe(tickers):
    dataset = pd.DataFrame()

    for ticker in tickers:
        df = get_stock_dataframe(ticker)
        if dataset.empty:
            dataset = df
        else:
            dataset = dataset.join(df, how="outer", on="Date")

    return dataset
