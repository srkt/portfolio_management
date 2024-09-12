import sys
from sqlalchemy import create_engine, func, Date
from sqlalchemy.orm import sessionmaker
import pandas as pd
import pandas_datareader as pdr
import yfinance as yf
import csv
import src.db.orm_tables as tables
from datetime import timedelta, date, datetime


sys.path.append("")
import config as cf
import src.db.stock_repository as sr

# Define the database connection
db_engine = create_engine(cf.DB_CONNECTION, echo=False)
Session = sessionmaker(bind=db_engine)
session = Session()


# Loads stock data for a given ticker from yfinance into database
def load_stock_data_into_db(ticker, start, end):
    yf.pdr_override()

    try:
        stocks_data = yf.download(ticker, start, end)
        stocks_data.insert(0, "Ticker", ticker)
        stocks_data.to_sql("stock_data", con=db_engine, if_exists="append")
        session.commit()
    except Exception as e:
        print("Error occurred loading " + ticker)
        print(str(e))
        session.rollback()


# Update ticker info table
def update_ticker_info_table(ticker):

    update_date = get_ticker_log(ticker)
    dt = update_date[0]

    session.query(tables.Tickers).filter(tables.Tickers.Ticker == ticker).update(
        {"Last_Update_Date": dt}
    )

    session.commit()
    print(ticker + " date  updated to : " + dt)


# Update ticker info table
def insert_ticker_info_table(ticker):
    db_engine.connect()
    update_date = get_ticker_log(ticker)
    ticker_info = tables.Tickers(Ticker=ticker, Last_Update_Date=update_date)
    session.add(ticker_info)
    session.commit()


def upsert_ticker(ticker):
    if has_ticker(ticker=ticker):
        print("Ticker found, updating " + ticker + " date")
        update_ticker_info_table(ticker)
    else:
        print("Ticker not found, inserting " + ticker + " date")
        insert_ticker_info_table(ticker)


def has_ticker(ticker):
    exists = (
        session.query(tables.Tickers.Ticker).filter_by(Ticker=ticker).first()
        is not None
    )
    return exists


# Retrives all tickers in database
def get_all_tickers_in_db():
    query = session.query(tables.Tickers.Ticker)
    result = session.execute(query)
    return [r for r, in result.fetchall()]


def get_last_update_stock_data(ticker):
    last_update_date = (
        session.query(tables.Tickers.Last_Update_Date).filter_by(Ticker=ticker).first()
    )
    # if last_update_date is not None:
    return last_update_date


def get_ticker_log(ticker):
    last_update_date = (
        session.query(tables.TickerLog.Last_Updated_On).filter_by(Ticker=ticker).first()
    )

    return last_update_date


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
def load_stock_data_into_db_from_file(
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
def get_stock_dataframe(ticker):
    condition = tables.StockData.Ticker == ticker

    query = session.query(
        tables.StockData.Adj_Close.label("Close"),
        func.date(tables.StockData.Date).label("Date"),
        tables.StockData.Volume,
    ).filter(condition)

    result = session.execute(query)
    df = pd.DataFrame(result.fetchall(), columns=["Close", "Date", "Volume"])
    df.set_index("Date", inplace=True)
    df.index = pd.to_datetime(df.index)
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


def get_adjusted_end_date():
    # Get the current datetime and time component
    now = datetime.now()
    current_time = now.time()

    # Define the time range (4 PM to 12 AM) // assuming yfinance will have data after market close on the day
    four_pm = now.replace(hour=16, minute=0, second=0, microsecond=0).time()
    midnight = now.replace(hour=23, minute=59, second=59, microsecond=999999).time()

    # Check if the current time is between 4 PM and midnight // if times falls between 4pm and 12am get todays date else yesterday date
    if four_pm <= current_time <= midnight:
        return now.date()  # Return the current day
    else:
        return now.date() - timedelta(days=1)  # Return the previous day


def are_dates_same_day(date1, date2):
    # Ensure that both inputs are of type 'date'
    if isinstance(date1, datetime):
        date1 = date1.date()  # Extract date part if it's a datetime object
    if isinstance(date2, datetime):
        date2 = date2.date()  # Extract date part if it's a datetime object

    # Compare the two date objects
    return date1 == date2


def hasLatestData(ticker):
    dt = get_ticker_log(ticker)

    if dt is None:
        return False

    latestDatadateInDb = datetime.strptime(dt[0], "%Y-%m-%d %H:%M:%S.%f")
    current_date = get_adjusted_end_date()

    return are_dates_same_day(latestDatadateInDb, current_date)


def get_new_data_time_frame(ticker):

    last_data_date = sr.get_ticker_log(ticker)

    if last_data_date is not None:
        try:
            last_update_date = datetime.strptime(
                last_data_date[0], "%Y-%m-%d %H:%M:%S.%f"
            )
            new_start_date = last_update_date + timedelta(days=1)
        except:
            last_update_date = datetime.strptime(last_data_date[0], "%Y-%m-%d")

    else:
        new_start_date = datetime.now() - timedelta(days=365)

    new_end_date = (
        datetime.now().date()
    )  # get_adjusted_end_date()  # datetime.now().date() + timedelta(days=-1)
    return [ticker, new_start_date, new_end_date]


def refresh_all_stocks():
    all_tickers = get_all_tickers_in_db()
    for ticker in all_tickers:
        if not hasLatestData(ticker):
            time_frame_ticker = get_new_data_time_frame(ticker)
            load_stock_data_into_db(
                ticker=time_frame_ticker[0],
                start=time_frame_ticker[1],
                end=time_frame_ticker[2],
            )
            upsert_ticker(time_frame_ticker[0])
            print("Stock data update for " + ticker + " completed...")

        else:
            print("Latest data already available for " + ticker)


def update_technical_analysis(ticker, df_tech_analysis):
    try:
        df_tech_analysis.insert(0, "Ticker", ticker)
        df_tech_analysis.to_sql(
            "STOCK_TECHNICAL_ANALYSIS", con=db_engine, if_exists="append"
        )
        session.commit()
    except Exception as e:
        print("Error occurred saving data of " + ticker)
        print(str(e))
        session.rollback()


def saveAvwapDataPoint(ticker, anchor_date, notes=None):

    new_entry = tables.MultiVwapPoints(
        Ticker=ticker, Anchor_Date=anchor_date, Notes=notes
    )
    session.add(new_entry)
    session.commit()  # Commit the transaction
    return new_entry.Id  # Return the primary key


def saveAvawpData(df):
    df.to_sql("AVWAP_DATA", con=db_engine, if_exists="append")
