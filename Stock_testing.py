import pandas as pd
import numpy as np
import yfinance as yf
import datetime as dt
from pandas_datareader import data as pdr
import seaborn as sn
import matplotlib.pyplot as plt

yf.pdr_override()

start = dt.datetime(2015, 1, 1)
end = dt.datetime.now()

tickers = ["BAKKA.OL", "SALM", "FB", "AAPL", "GOOG"]

df = pdr.get_data_yahoo(tickers, start, end)["Adj Close"]

cov_matrix = df.pct_change().apply(lambda x: np.log(1+x)).cov()
corr_matrix = df.pct_change().apply(lambda x: np.log(1+x)).corr()

round_val = 2

ticker_returns = []
std = []
max_pct = []
min_pct = []

for c in df.columns:
    ticker_returns.append(round(df[c].pct_change().mean() * 100, round_val))
    std.append(round((df[c].pct_change().std()) * 100, round_val))
    max_pct.append(round(df[c].pct_change().max() * 100, round_val))
    min_pct.append(round(df[c].pct_change().min() * 100, round_val))


data = {"Average Return": ticker_returns, "Standard Deviation": std, "Max Percent": max_pct, "Min Percent": min_pct}
mainInfo = pd.DataFrame(data, columns = ["Average Return", "Standard Deviation", "Max Percent", "Min Percent"], index = sorted(tickers))

print()
print("The main info:")
print(mainInfo)
print()
print("Correlation Matrix:")
print(corr_matrix)


sn.heatmap(corr_matrix, annot = True)


ind_er = df.resample("Y").last().pct_change().mean()
# print(ind_er)

p_ret = []
p_vol = []
p_weights = []

num_assets = len(df.columns)
num_p = 10000

for p in range(num_p):
    weights = np.random.random(num_assets)
    weights = weights / np.sum(weights)
    p_weights.append(weights)

    returns = np.dot(weights, ind_er)
    p_ret.append(returns)

    var = cov_matrix.mul(weights, axis = 0).mul(weights, axis = 1).sum().sum()
    sd = np.sqrt(var)

    ann_sd = sd * np.sqrt(250)
    p_vol.append(ann_sd)

p_data = {"Returns": p_ret, "Volatility": p_vol}
p_data = pd.DataFrame(p_data)

for counter, symbol in enumerate(df.columns.tolist()):
    p_data[symbol + " weight"] = [w[counter] for w in p_weights]

portfolios = pd.DataFrame(p_data)
# print(portfolios)

min_vol_port = portfolios.iloc[portfolios["Volatility"].idxmin()]

print()
print("Minimum volatility return: " + str(round(min_vol_port[0], round_val)))
print("Minimum volatility: " + str(round(min_vol_port[1], round_val)))
print()
print("Minimum volatility weighing: ")
print(str(round(min_vol_port[2:], round_val)))

rf = 0.003
optimal_risk_p = portfolios.iloc[((portfolios["Returns"]-rf)/portfolios["Volatility"]).idxmax()]

print()
print("Optimal return: " + str(round(optimal_risk_p[0], round_val)))
print("Optimal volatility: " + str(round(optimal_risk_p[1], round_val)))
print()
print("Optimal weighing: ")
print(str(round(optimal_risk_p[2:], round_val)))

plt.subplots(figsize = [10,10])
plt.scatter(portfolios["Volatility"], portfolios["Returns"], marker = "o", s = 10, alpha = 0.3)
plt.scatter(min_vol_port[1], min_vol_port[0], color = "r", marker = "*", s = 125)
plt.scatter(optimal_risk_p[1], optimal_risk_p[0], color = "g", marker = "*", s = 125)

plt.show()