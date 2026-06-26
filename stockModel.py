from datetime import date, timedelta
import sys
from sklearn.model_selection import train_test_split
import yfinance as yf
import requests
import pandas as pd
from bs4 import BeautifulSoup
from sklearn.ensemble import RandomForestRegressor
import joblib

def get_finviz_tickers():
        otherTickers = []
        url = "https://finviz.com/screener?v=111&s=ta_toplosers&f=ind_stocksonly%2Csh_avgvol_o1000%2Csh_price_o5%2Cta_change_d5"
        headers = {"User-Agent": "Mozilla/5.0"}

        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        rows = soup.select("tr")
        for row in rows:
            cols = row.find_all("td")
            if(len(cols) < 2):
                continue
            try:
                ticker = cols[1].text.strip()
                tickerRows = ticker.split()
                for line in tickerRows:
                    if(line.isalpha() and line.isupper() and line != "ETF" and line != "USA" and len(ticker) <=5):
                        otherTickers.append([date.today().isoformat(), line])
            except:
                continue
        otherTickers = pd.DataFrame(otherTickers, columns=["Date", "Ticker"])
        return otherTickers

def get_tickers():
    usrinput = input("Type 1 if you want to train the model with the dataset or type 0 to use today's and previous data (ONLY AFTER 4:00 PM).")
    dataTickers = pd.DataFrame()
    otherTickers = []
    if usrinput == "0":
        otherTickers = get_finviz_tickers()
    dataTickers = pd.read_csv("historicalDataTickers.txt", sep="\t")
    print("read csv")
    dataTickers = dataTickers.drop(["Change %", "Stock Exchange"], axis=1)
    if isinstance(otherTickers, pd.DataFrame):
        dataTickers = pd.concat([dataTickers, otherTickers], ignore_index=True)
    otherInput = input("Enter other ticker and enter date (YYYY-MM-DD) (space separated) or type 0 to not enter any: ")
    while otherInput != "0":
        otherInput = otherInput.split()
        if len(otherInput) == 2:
            new_row = pd.DataFrame([[otherInput[1], otherInput[0]]], columns=["Date", "Ticker"])
            dataTickers = pd.concat([dataTickers, new_row], ignore_index=True)
        otherInput = input("Enter other ticker and enter date (YYYY-MM-DD) (space separated) or type 0 to not enter any: ")
    print(dataTickers)
    return dataTickers


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
  START_TIME = 20
  tableRows = []
  for m in range(START_TIME, len(table) - AHEAD_TIME):
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
  return pd.DataFrame(tableRows)

if __name__ == "__main__":
    #Main Loop to build data
    selectedTickers = get_tickers().drop_duplicates()
    data = []
    for row in selectedTickers.itertuples(index=True):
        t = row.Ticker
        print("Putting Data for: ", t)
        dataTable = yf.download(tickers=t, start=row.Date,end=(date.fromisoformat(row.Date)+timedelta(days=1)).isoformat(), interval="1m", progress=False)
        if(dataTable is None or len(dataTable) <50):
            print("Error: No data available for the selected ticker: ", t)
            continue
        if isinstance(dataTable.columns, pd.MultiIndex):
            dataTable.columns = dataTable.columns.droplevel(1)
        dataTable = dataTable.dropna()
        if(populate_data(t, dataTable).empty or populate_data(t, dataTable) is None):
            print("Could not populate data for", t)
        else:
         data.append(populate_data(t, dataTable))
        fullDataset = pd.concat(data, ignore_index=True)

    X = fullDataset[["return_1", "return_5", "daily_range", "body_pct", "volatility", "vol_ratio", "volume", "upper_wick", "lower_wick", "minutes_after_open"]]

    y = fullDataset["target_return"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    model = RandomForestRegressor(n_estimators=200, max_depth=10)
    model.fit(X_train, y_train)
    print("Score: ", model.score(X_test, y_test))
    joblib.dump(model, "stock_model.pkl")
