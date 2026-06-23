import sys
from sklearn.model_selection import train_test_split
import yfinance as yf
import requests
import pandas
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


#Returns a DataFrame with the populated data with the parameters as the ticker and the table with the ticker data
def populate_data(t, table):
  table["return_1"] = table["Close"].pct_change()
  table["return_5"] = table["Close"].pct_change(periods=5)
  table["daily_range"] = table["High"] - table["Low"]
  table["body"] = table["Close"] - table["Open"]
  table["body_pct"] = table["body"] / table["Open"]
  table["volatility"] = table["return_1"].rolling(10).std()
  table["vol_ma"] = table["volatility"].rolling(10).mean()
  table["vol_ratio"] = table["Volume"] / table["vol_ma"]
  table["upper_wick"] = table["High"] - table[["Open", "Close"]].max(axis=1)
  table["lower_wick"] = table[["Open", "Close"]].min(axis=1) - table["Low"]
  AHEAD_TIME = 60
  tableRows = []
  for m in range(20, len(table) - AHEAD_TIME):
      current = table.iloc[m]
      currentPrice = current["Close"]
      futureWindow = table.iloc[m:m + AHEAD_TIME]
      futureMax = futureWindow["High"].max()
      timeMax = futureWindow.idxmax()
      potentialGain = (futureMax - currentPrice)/currentPrice

      tableRows.append({
          "ticker": t,
          "potential_gain": potentialGain,
          "volatility": current["volatility"],
          "body_pct": current["body_pct"],
          "daily_range": current["daily_range"],
          "vol_ma": current["vol_ma"],
          "vol_ratio": current["vol_ratio"],
          "volume": current["Volume"],
          "upper_wick": current["upper_wick"],
          "lower_wick": current["lower_wick"],
          "return_1": current["return_1"],
          "return_5": current["return_5"],
          "minutes_after_open": m,
          "target_return": potentialGain
      })
  return pandas.DataFrame(tableRows)


#Main Loop to build data
selectedTickers = get_tickers()
data = []
for t in selectedTickers:
  print("Putting Data for: ", t)
  dataTable = yf.download(tickers=t, period="1d", interval="1m", progress=False)
  if(dataTable is None or len(dataTable) <50):
    print("Error: No data available for the selected tickers.")
    sys.exit(1)
  dataTable.columns = [col[0] for col in dataTable.columns]
  dataTable = dataTable.dropna()
  if(populate_data(t, dataTable).empty or populate_data(t, dataTable) is None):
    print("Could not populate data for", t)
  else:
   data.append(populate_data(t, dataTable))
  fullDataset = pandas.concat(data, ignore_index=True)

X = fullDataset[["return_1", "return_5", "daily_range", "body_pct", "volatility", "vol_ratio", "volume", "upper_wick", "lower_wick", "minutes_after_open"]]

y = fullDataset["target_return"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
model = RandomForestRegressor(n_estimators=200, max_depth=10)
model.fit(X_train, y_train)
print("Score: ", model.score(X_test, y_test))
joblib.dump(model, "stock_model.pkl")
