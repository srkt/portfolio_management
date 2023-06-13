import sys
import unittest


sys.path.append("")

import src.app.portfolio_optimization as pf
import src.db.stock_repository as sr
import src.app.optimizers.sharpe as sharpe


class OptimizerSpecs(unittest.TestCase):
    def test_sharpe_optimization(self):
        tickers = sr.get_all_tickers_in_db()
        # tickers = ["TSLA", "AVGO", "LLY", "MSFT", "NOW"]
        portfolio = pf.Portfolio(tickers)
        portfolio.optimize_using_sharpe(risk_free_rate=0.1 / 365)


unittest.main()
