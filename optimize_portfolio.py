import pandas as pd
import yfinance as yf
import numpy as np
import scipy.optimize as sco
import matplotlib.pyplot as plt


# Define the tickers and the desired date range
tickers = ["AAPL", "GOOGL", "MSFT", "AMZN", "META", "TSLA", "NVDA", "JPM", "V", "JNJ"]
start_date = "2013-01-01"
end_date = "2023-06-10"

# Get historical stock data using yfinance
data = yf.download(tickers, start=start_date, end=end_date)["Adj Close"]

# Calculate daily returns
returns = data.pct_change().dropna()


# function returns negative so we can minimize it. Its equivalent to maximizing positive sharpe ratio
def sharpe_ratio(weights, returns):
    weights = np.array(weights)
    portfolio_returns = np.dot(returns, weights)
    portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(returns.cov(), weights)))
    sharpe_ratio = portfolio_returns.mean() / portfolio_volatility
    return -sharpe_ratio


# Initial weights
initial_weights = np.repeat(1 / len(tickers), len(tickers))

# Set the constraints for the optimization
constraints = {"type": "eq", "fun": lambda x: np.sum(x) - 1}

# Set the bounds for the weights (0 <= weight <= 1)
bounds = tuple((0, 1) for _ in range(len(tickers)))

# Perform the optimization
result = sco.minimize(
    sharpe_ratio,
    initial_weights,
    args=(returns,),
    method="SLSQP",
    bounds=bounds,
    constraints=constraints,
)

# In[121]:


optimized_weights = result.x


# In[125]:


portfolio_returns = np.dot(returns, optimized_weights)
portfolio_volatility = np.sqrt(
    np.dot(optimized_weights.T, np.dot(returns.cov(), optimized_weights))
)
portfolio_sharpe_ratio = portfolio_returns.mean() / portfolio_volatility


# In[129]:


# Print the optimized weights and portfolio statistics

print("Optimized Weights:")
for ticker, weight in zip(tickers, optimized_weights):
    print(f"{ticker}: {weight:.2f}")

print("\nPortfolio Statistics:")
print(f"Expected Annual Return: { portfolio_returns.mean() * 252 :.2%}")
print(f"Annual Volatility: { portfolio_volatility * np.sqrt(252) :.2%}")
print(f"Sharpe Ratio: {portfolio_sharpe_ratio:.2f}")
