import joblib
import pandas as pd
from stockModel import fullDataset
model = joblib.load("stock_model.pkl")
stocks = pd.DataFrame(columns=["ticker", "date"])
userinput = input("Enter 1 to scrape finviz for daily losses, or 2 to enter data with ticker with date: ")
if userinput == "2":
    while userinput != 0:
        userinput = input("Enter ticker and date (e.g. AAPL 2023-01-01) or 0 to stop: ")
data = fullDataset.copy()
features = data[["return_1", "return_5", "daily_range", "body_pct", "volatility", "vol_ratio", "volume", "upper_wick", "lower_wick", "minutes_after_open"]]
data["Score"] = model.predict(features)
# with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    
#  print(data.sort_values("Score", ascending=False))
with open("predictionText.txt", "w") as f:
    f.write(data.sort_values("Score", ascending=False).to_string(index=False))