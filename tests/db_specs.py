import sys
import unittest

sys.path.append("")

import src.db.stock_repository as sr


class DbSpecs(unittest.TestCase):
    def test_data_load(self):
        # tickers = sr.get_tickers_from_file("symbols.csv")
        tickers = sr.get_all_tickers_in_db()
        self.assertIsNotNone(tickers)


unittest.main()
