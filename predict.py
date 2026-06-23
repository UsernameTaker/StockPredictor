import joblib
import pandas as pd
from stockModel import fullDataset
model = joblib.load("stock_model.pkl")
data = fullDataset.copy()
features = data[["return_1", "return_5", "daily_range", "body_pct", "volatility", "vol_ratio", "volume", "upper_wick", "lower_wick", "minutes_after_open"]]
data["Score"] = model.predict(features)
# with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    
#  print(data.sort_values("Score", ascending=False))
with open("predictionText.txt", "w") as f:
    f.write(data.sort_values("Score", ascending=False).to_string(index=False))