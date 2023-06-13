import pandas as pd
import yfinance as yf
import numpy as np
import scipy.optimize as sco
from itertools import combinations

import src.db.stock_repository as sr
import src.app.optimizers.sharpe as sharpe


class Portfolio:
    def __init__(self, tickers):
        # Define the tickers
        self.tickers = tickers

    # Annual risk free rate in percent
    annual_risk_free_rate = 0.04

    def _set_data(self, data):
        self.data = data
        self.changes = self.data.pct_change().dropna()

    def load_data(self, start_date=None, end_date=None):
        data = sr.get_adj_close_dataframe(self.tickers)
        self._set_data(data)

    def get_portfolio_returns(self, weights, returns):
        portfolio_returns = np.dot(returns, weights)
        return portfolio_returns

    def get_portfolio_volatility(self, weights, returns):
        portfolio_volatility = np.sqrt(
            np.dot(weights.T, np.dot(returns.cov(), weights))
        )
        return portfolio_volatility

    # Select combination within portfolio for better sharpe ratio.

    def select_stocks(stocks, num_to_select):
        all_combinations = list(combinations(stocks, num_to_select))
        return all_combinations

    def optimize_using_sharpe(
        self, risk_free_rate=0.04, start_date=None, end_date=None
    ):
        self.load_data(start_date, end_date)
        # initial_weights = np.repeat(1 / len(self.tickers), len(self.tickers))
        shrp = sharpe.Sharpe(self.tickers, self.changes)
        shrp.annual_risk_free_rate = risk_free_rate
        shrp.optimize()
