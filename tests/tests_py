import pandas as pd

from data_load import get_ticker_data, get_tickers
from portfolio_optimization import Portfolio

# print("loading started...")
# load_symbols_into_db()
# print("loading complete")

# get_stocks_data("WMT", "2013-01-01", "2023-06-09")
dataset = pd.DataFrame()
tickers = get_tickers()

for ticker in tickers:
    df = get_ticker_data(ticker)
    if dataset.empty:
        dataset = df
    else:
        dataset = dataset.join(df, how="outer", on="Date")

print(dataset.tail())

start_date = "2013-01-01"
end_date = "2023-06-10"

pfolio = Portfolio(tickers, start_date, end_date)
pfolio.annual_risk_free_rate = 4 / (100 * 365)
pfolio.set_data(dataset)
pfolio.get_optimal_data()
