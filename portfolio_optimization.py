import pandas as pd
import yfinance as yf
import numpy as np
import scipy.optimize as sco
from itertools import combinations

# import matplotlib.pyplot as plt


class Portfolio:
    def __init__(self, tickers, start_date, end_date):
        # Define the tickers and the desired date range
        self.tickers = tickers
        self.start_date = start_date
        self.end_date = end_date

    # Annual risk free rate in percent
    annual_risk_free_rate = 0.04

    # Get historical stock data using yfinance
    def get_data(self):
        data = yf.download(self.tickers, start=self.start_date, end=self.end_date)[
            "Adj Close"
        ]

        self.set_data(data)
        # self.changes = self.data.pct_change().dropna()

    def set_data(self, data):
        self.data = data
        self.changes = self.data.pct_change().dropna()

    def get_portfolio_returns(self, weights, returns):
        portfolio_returns = np.dot(returns, weights)
        return portfolio_returns

    def get_portfolio_volatility(self, weights, returns):
        portfolio_volatility = np.sqrt(
            np.dot(weights.T, np.dot(returns.cov(), weights))
        )
        return portfolio_volatility

    def negative_sharpe_ratio(self, weights, returns):
        weights = np.array(weights)
        portfolio_returns = np.dot(returns, weights)
        portfolio_volatility = np.sqrt(
            np.dot(weights.T, np.dot(returns.cov(), weights))
        )
        sharpe_ratio = portfolio_returns.mean() / portfolio_volatility
        return -sharpe_ratio

    def optimize_weights(self, tickers):
        # Initial weights
        initial_weights = np.repeat(1 / len(tickers), len(tickers))

        # Set the constraints for the optimization
        constraints = {"type": "eq", "fun": lambda x: np.sum(x) - 1}

        # Set the bounds for the weights (0 <= weight <= 1)
        bounds = tuple((0, 1) for _ in range(len(tickers)))

        # Perform the optimization
        result = sco.minimize(
            self.negative_sharpe_ratio,
            initial_weights,
            args=(self.changes),
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
        )

        return result.x

    def optimized_portfolio_values(self, returns, optimized_weights, risk_free_rate=0):
        portfolio_returns = np.dot(returns, optimized_weights)
        portfolio_volatility = np.sqrt(
            np.dot(optimized_weights.T, np.dot(returns.cov(), optimized_weights))
        )
        portfolio_sharpe_ratio = (
            portfolio_returns.mean() - risk_free_rate
        ) / portfolio_volatility
        return (portfolio_returns, portfolio_volatility, portfolio_sharpe_ratio)

    def get_optimal_data(self):
        optimized_weights = self.optimize_weights(self.tickers)  # result.x
        # risk_free_rate = 0.04/365
        (
            portfolio_returns,
            portfolio_volatility,
            portfolio_sharpe_ratio,
        ) = self.optimized_portfolio_values(
            self.changes, optimized_weights, self.annual_risk_free_rate
        )

        print("Optimized Weights:")
        for ticker, weight in zip(self.tickers, optimized_weights):
            print(f"{ticker}: {weight:.2f}")

        print("\nPortfolio Statistics:")
        print(f"Expected Annual Return: { portfolio_returns.mean() * 252 :.2%}")
        print(f"Annual Volatility: { portfolio_volatility * np.sqrt(252) :.2%}")
        print(f"Sharpe Ratio: {portfolio_sharpe_ratio  * np.sqrt(252) :.2f}")


# tickers = ["AAPL", "GOOGL", "MSFT", "AMZN", "META", "TSLA", "NVDA", "JPM", "V", "JNJ"]
# start_date = "2013-01-01"
# end_date = "2023-06-10"

# pfolio = Portfolio(tickers, start_date, end_date)
# pfolio.annual_risk_free_rate = 4 / (100 * 365)
# pfolio.get_data()
# pfolio.get_optimal_data()

# In[ ]:


# # Select combination within portfolio for better sharpe ratio.
# def select_stocks(stocks, num_to_select):
#     all_combinations = list(combinations(stocks, num_to_select))
#     return all_combinations

# # Example usage:
# available_stocks = ["AAPL", "GOOGL", "MSFT", "AMZN", "FB", "TSLA", "NVDA", "JPM", "V", "JNJ"]
# selected_stocks = select_stocks(available_stocks, 5)

# # Print the selected stock combinations
# for combination in selected_stocks:
#     print(combination)


# # In[ ]:
