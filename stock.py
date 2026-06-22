import yfinance as yf
import requests
import pandas as pd
from bs4 import BeautifulSoup
from sklearn.ensemble import RandomForestRegressor
import joblib
def get_tickers():
    url = "https://finviz.com/screener?v=111&s=ta_toplosers&f=ind_stocksonly%2Csh_avgvol_o1000%2Csh_price_o5%2Cta_change_d5"
    headers = {"User-Agent": "Mozilla/5.0"}

    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    rows = soup.select("tr")
    tickers = []
    for row in rows:
        cols = row.find_all("td")
        # print(row)
        # print("______________________________________________________")
        if(len(cols) < 2):
            continue
        try:
            ticker = cols[1].text.strip()
            tickerRows = ticker.split()
            for line in tickerRows:
                if(line.isalpha() and line.isupper() and line != "ETF" and line != "USA" and len(ticker) <=5):
                    tickers.append(line)


        except:
            continue
    selectedTickers = list(set(tickers))
    print(selectedTickers)
    return selectedTickers


data = []
for t in selectedTickers:
  #print(t)
  dataTable = yf.download(tickers=t, period="1d", interval="1m", progress=False)
  if(dataTable is None or len(dataTable) <50):
    print("Error: No data available for the selected tickers.")
  dataTable = dataTable.dropna()
  table = dataTable.copy()
  #print("hi")
  #print(table)
  #print(len(table))
#   print(table)
#   print("______________")
  AHEAD_TIME = 60
  for m in range(0, len(table) - AHEAD_TIME):
      currentPrice = table["Close"].iloc[m]
      futureWindow = table["Close"].iloc[m:m + AHEAD_TIME]
      futureMax = futureWindow.max()
      timeMax = futureWindow.idxmax()
      potentialGain = (futureMax - currentPrice)/currentPrice

      data.append({
          "ticker": t,
          "current_price": currentPrice,
          "future_max": futureMax,
          "time_max": timeMax,
          "potential_gain": potentialGain,
          "volatility": table["Close"].pct_change().rolling(10).std().iloc[m],
          "volume": table["Volume"].iloc[m],
          "return_5": table["Close"].pct_change().iloc[m],
          "return_10": table["Close"].pct_change().iloc[m]
      })
              
      


#print(rows)
#print(r.text)

#ticker = "AAPL"
#data = yf.download(tickers=ticker, period="1d", interval="1h", prepost=True)
# a = input("Enter tickers: ")
# print(a)
# badTickers = [x for x in tickers if  yf.Ticker(x).history(period="1d").empty or yf.Ticker(x).fast_info.last_price <=5]
# print("got bad tickers!")
# for b in badTickers:
#     tickers.discard(b)
# # for t in tickers:
# #     ticker = yf.Ticker(t)
# #     try:
# #      if(ticker.fast_info.last_price <= 5):
# #         tickers.discard(t)
# #     except:
# #       tickers.discard(t);

# print(tickers)
# dataTable = pd.read_html('https://finance.yahoo.com/markets/stocks/losers/')
# table = dataTable[0]
# print(table.head())
