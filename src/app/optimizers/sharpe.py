import pandas as pd
import yfinance as yf
import numpy as np
import scipy.optimize as sco


class Sharpe:
    def __init__(self, tickers, data):
        # Define the tickers and percentage change data
        self.tickers = tickers
        self.data = data

    # Annual risk free rate in percent
    annual_risk_free_rate = 0

    def _calculate_negative_sharpe_ratio(self, weights, returns):
        weights = np.array(weights)
        portfolio_returns = np.dot(returns, weights)
        portfolio_volatility = np.sqrt(
            np.dot(weights.T, np.dot(returns.cov(), weights))
        )
        sharpe_ratio = portfolio_returns.mean() / portfolio_volatility
        return -sharpe_ratio

    def _optimize_weights(self):
        # Initial weights
        initial_weights = np.repeat(1 / len(self.tickers), len(self.tickers))

        # Set the constraints for the optimization
        constraints = {"type": "eq", "fun": lambda x: np.sum(x) - 1}

        # Set the bounds for the weights (0 <= weight <= 1)
        bounds = tuple((0, 1) for _ in range(len(self.tickers)))

        # Perform the optimization
        result = sco.minimize(
            self._calculate_negative_sharpe_ratio,
            initial_weights,
            args=(self.data),
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
        )

        return result.x

    def _optimized_portfolio_values(self, returns, optimized_weights, risk_free_rate=0):
        portfolio_returns = np.dot(returns, optimized_weights)
        portfolio_volatility = np.sqrt(
            np.dot(optimized_weights.T, np.dot(returns.cov(), optimized_weights))
        )
        portfolio_sharpe_ratio = (
            portfolio_returns.mean() - risk_free_rate
        ) / portfolio_volatility
        return (portfolio_returns, portfolio_volatility, portfolio_sharpe_ratio)

    def optimize(self):
        optimized_weights = self._optimize_weights()  # result.x
        # risk_free_rate = 0.04/365
        (
            portfolio_returns,
            portfolio_volatility,
            portfolio_sharpe_ratio,
        ) = self._optimized_portfolio_values(
            self.data, optimized_weights, self.annual_risk_free_rate
        )

        print("Optimized Weights:")
        for ticker, weight in zip(self.tickers, optimized_weights):
            if abs(weight) > 1e-10:
                print(f"{ticker}: {weight*100:.2f}%")

        print("\nPortfolio Statistics:")
        print(f"Expected Annual Return: { portfolio_returns.mean() * 252 :.2%}")
        print(f"Annual Volatility: { portfolio_volatility * np.sqrt(252) :.2%}")
        print(f"Sharpe Ratio: {portfolio_sharpe_ratio  * np.sqrt(252) :.2f}")
