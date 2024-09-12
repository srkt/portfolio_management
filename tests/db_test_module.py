import sys
import unittest
from datetime import timedelta, date, datetime

sys.path.append("")

import src.db.stock_repository as sr
import src.app.analysis.technical_analysis as ta


class TestDbSpecs(unittest.TestCase):
    def test_data_load(self):
        # tickers = sr.get_tickers_from_file("symbols.csv")
        tickers = sr.get_all_tickers_in_db()
        self.assertIsNotNone(tickers)

    def test_check_for_ticker(self):
        ticker_exists = sr.has_ticker("NVDA")
        self.assertIsNotNone(ticker_exists)
        print(ticker_exists)

    def test_refresh_data(self):
        sr.refresh_all_stocks()

    def get_data(self):
        ticker = "NVDA"
        df = sr.get_stock_dataframe(ticker)
        print(df.tail())

    def calculate_sma(self):
        ticker = "NVDA"
        df = sr.get_stock_dataframe(ticker)
        sma = ta.calculate_sma(df, 5)
        print(sma.tail(20))

    def calculate_multi_sma(self):
        ticker = "CAVA"
        df = sr.get_stock_dataframe(ticker)
        sma = ta.calculate_multi_sma(df)
        print(sma.tail(20))

    def calculate_vwap(self):
        ticker = "NVDA"
        df = sr.get_stock_dataframe(ticker)
        vwap = ta.VWAP(df)
        print(vwap.tail(20))

    def calculate_multiple_indicators(self):
        ticker = "CAVA"
        df = sr.get_stock_dataframe(ticker)
        df = ta.calculate_multi_sma(df)
        df = ta.VWAP(df)
        print(df.tail(5))

    def calculate_avwap(self):
        ticker = "NVDA"
        df = sr.get_stock_dataframe(ticker)
        adt = datetime.strptime("2024-09-08", "%Y-%m-%d")
        vwap = ta.Anchored_VWAP(df, adt)
        print(vwap.tail(20))

    def calculate_technical_analysis(self):
        ticker = "NVDA"
        df = ta.get_technical_analysis(ticker)
        print(df.tail(10))

    def update_technical_analysis(self):
        ticker = "NVDA"
        ta.update_technical_analysis(ticker)

    def save_avwap_data(self):
        ticker = "CAVA"
        anchor_date = "2024-08-23"
        ta.saveAvwapData(ticker, anchor_date)


if __name__ == "__main__":
    unittest.main()
