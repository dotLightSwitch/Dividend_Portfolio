import yfinance as yf
import pandas as pd
import numpy as np
import datetime as dt
from pandas_datareader import data
import pandas_datareader as pdr
from get_all_tickers import get_tickers as gt
import requests
import bs4
from bs4 import BeautifulSoup

yf.pdr_override()
tickers = gt.get_tickers(NYSE = True, NASDAQ = False, AMEX = False)[:100]

droplist_tickers = ["ASGI", "AEB", "ABM"]

tickers = list(filter(lambda x: x not in droplist_tickers, tickers))

# tickers = ["JNJ", "KO", "AAPL", "MMM", "FB"]

print("Checking " + str(len(tickers)) + " different tickers.")

def get_info_from_yahoo(ticker):
    URL = f"https://finance.yahoo.com/quote/{ticker}/key-statistics?p={ticker}"
    try:
        page = requests.get(URL)
        soup = BeautifulSoup(page.text, "html.parser")

        div_yield = soup.select(r"#Col1-0-KeyStatistics-Proxy > section > div.Mstart\(a\).Mend\(a\) > div.Fl\(end\).W\(50\%\).smartphone_W\(100\%\) > div > div:nth-child(3) > div > div > table > tbody > tr:nth-child(2) > td.Fw\(500\).Ta\(end\).Pstart\(10px\).Miw\(60px\)")
        div_yield = div_yield[0].text.strip()

        pay_ratio = soup.select(r"#Col1-0-KeyStatistics-Proxy > section > div.Mstart\(a\).Mend\(a\) > div.Fl\(end\).W\(50\%\).smartphone_W\(100\%\) > div > div:nth-child(3) > div > div > table > tbody > tr:nth-child(6) > td.Fw\(500\).Ta\(end\).Pstart\(10px\).Miw\(60px\)")
        pay_ratio = pay_ratio[0].text.strip()

        # FIND DIVIDEND YIELD
        if div_yield == "N/A":
            div_yield = 0
        else:
            div_yield = float(div_yield[:-1])

        # FIND PAYOUT RATIO
        if pay_ratio == "N/A":
            pay_ratio = 0
        else:
            pay_ratio = float(pay_ratio[:-1])

        print(f"{ticker}... 33%")

        return [div_yield, pay_ratio]

    except Exception as e:
        print(f"Could not find dividend information on {ticker}")
        print(f"Error: {e}")
        return [0, 0]

def get_return_info(ticker):
    start_date = dt.datetime.now() - dt.timedelta(days = 7 * 365)
    end_date = dt.datetime.now()
    ticker_df = pdr.get_data_yahoo(ticker, start_date, end_date)["Adj Close"]

    ticker_pct = ticker_df.pct_change() * 100

    rval = 3
    avg_return = round(ticker_pct.mean(), rval)
    std = round(ticker_pct.std(), rval)
    max_return = round(ticker_pct.max(), rval)
    min_return = round(ticker_pct.min(), rval)

    print(f"{ticker}... 66%")

    return [avg_return, std, max_return, min_return]

def get_profile_info(ticker):
    URL = f"https://finance.yahoo.com/quote/{ticker}/profile?p={ticker}"
    try:
        page = requests.get(URL)
        soup = BeautifulSoup(page.text, "html.parser")

        sector = soup.select("#Col1-0-Profile-Proxy > section > div.asset-profile-container > div > div > p.D\(ib\).Va\(t\) > span:nth-child(2)")
        sector = sector[0].text
        print(f"{ticker}... 100%")
        return sector

    except Exception as e:
        print(f"Could not find profile information on {ticker}")
        print(f"Error: {e}")
        return "N/A"

low_yield = 2.6
high_yield = 7

max_pay_rate = 95

df_tickers = []
df_div_yield = []
df_payout_ratio = []

df_avg_return = []
df_std = []
df_max_return = []
df_min_return = []

df_sector = []

i = 0

for i in range(len(tickers)):
    ticker = tickers[i]

    info_from_stat = get_info_from_yahoo(ticker)
    div_yield = info_from_stat[0]
    payout_ratio = info_from_stat[1]

    if low_yield < div_yield < high_yield:
        cond_1 = True
    else: cond_1 = False

    if 1 < payout_ratio < max_pay_rate:
        cond_2 = True
    else: cond_2 = False

    # ADD EVERYTHING NEEDED FOR MAIN INFO
    if cond_1 and cond_2:

        info_from_return = get_return_info(ticker)
        avg_return = info_from_return[0]
        std = info_from_return[1]
        max_return = info_from_return[2]
        min_return = info_from_return[3]

        info_from_profile = get_profile_info(ticker)
        sector = info_from_profile

        df_tickers.append(ticker)
        df_sector.append(sector)
        df_div_yield.append(div_yield)
        df_payout_ratio.append(payout_ratio)

        df_avg_return.append(avg_return)
        df_std.append(std)
        df_max_return.append(max_return)
        df_min_return.append(min_return)
    
    i += 1

    if i % 10 == 0:
        print()
        print(str(i) + " tickers done.")
        print()

d = {"Ticker": df_tickers, "Sector": df_sector, 
    "Dividend Yield": df_div_yield, "Payout Ratio": df_payout_ratio,
    "Average Return": df_avg_return, "Standard Deviation": df_std, 
    "Max Return": df_max_return, "Min Return": df_min_return
}
df = pd.DataFrame(d)
print(df)
