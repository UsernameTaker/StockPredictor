import os

import joblib
from datetime import date, timedelta
import yfinance as yf
import pandas as pd
from stockModel import get_finviz_tickers, populate_data
if __name__ == "__main__":
    model = joblib.load("stock_model.pkl")
    stocks = pd.DataFrame(columns=["Date", "Ticker", "Minutes_After_Open"])
    userinput = input("Enter 1 to scrape finviz for daily losses, or 0 to skip:")
    if userinput == "1":
        otherTickers = get_finviz_tickers()
        inputTime = int(input("Enter the minutes after open to consider, or just type 0 to take the complete day data so far: "))
        if inputTime != 0 and inputTime > 0 and inputTime < 390:
            otherTickers["Minutes_After_Open"] = inputTime
        else:
            print("Invalid input. Please enter a valid number of minutes.")
            otherTickers["Minutes_After_Open"] = 20
        stocks = pd.concat([stocks, otherTickers], ignore_index=True)
    input_ticker = input("Enter a ticker symbol and a date (YYYY-MM-DD) and the minutes after open (space separated) or enter 0 to skip: ")
    while input_ticker != "0":
        input_ticker = input_ticker.split()
        if len(input_ticker) == 3:
            new_row = pd.DataFrame([[input_ticker[1], input_ticker[0], int(input_ticker[2])]], columns=["Date", "Ticker", "Minutes_After_Open"])
            stocks = pd.concat([stocks, new_row], ignore_index=True)
        input_ticker = input("Enter a ticker symbol and a date (YYYY-MM-DD) and the minutes after open (space separated) or enter 0 to skip: ")

    selectedTickers = stocks.drop_duplicates()
    data = []
    for row in selectedTickers.itertuples(index=True):
        t = row.Ticker
        print("Putting Data for: ", t)
        dataTable = yf.download(tickers=t, start=row.Date,end=(date.fromisoformat(row.Date)+timedelta(days=1)).isoformat(), interval="1m", progress=False)
        if(dataTable is None or len(dataTable) <10):
            print("Error: No data available for the selected ticker: ", t)
            continue
        if isinstance(dataTable.columns, pd.MultiIndex):
            dataTable.columns = dataTable.columns.droplevel(1)
        dataTable = dataTable.dropna()
        table = dataTable
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
        for m in range(row.Minutes_After_Open, len(table) - AHEAD_TIME):
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
            tickerData = pd.DataFrame(tableRows)
        if(tickerData.empty or tickerData is None):
            print("Could not populate data for", t)
        else:
         data.append(tickerData)
    data = pd.concat(data, ignore_index=True)
    features = data[["return_1", "return_5", "daily_range", "body_pct", "volatility", "vol_ratio", "volume", "upper_wick", "lower_wick", "minutes_after_open"]]
    data["Score"] = model.predict(features)
    # with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
        
    #  print(data.sort_values("Score", ascending=False))
    folder_path = "predictions"
    file_count = len([f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))])
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    with open("predictions/" + "prediction" + str(file_count+1) + ".txt", "w", encoding="utf-8") as file:
        file.write(data.sort_values("Score", ascending=False).to_string(index=False))