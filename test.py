import yfinance as yf
from datetime import date, timedelta
from stockModel import get_tickers
import pandas as pd
import os
if __name__ == "__main__":

 folder_path = "predictions"
 file_count = len([f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))])
#  directory = "predictions/"
#  filename = "prediction" + str(file_count+1) + ".txt"
#  if not os.path.exists(directory):
#     os.makedirs(directory)
 with open("predictions/" + "prediction" + str(file_count+1) + ".txt", "w", encoding="utf-8") as file:
    file.write("Hello, World!\n")
    file.write("This is a new line.")
    # dater = "2026-06-11"
    # tickers = ["AADX", "SDOT"]
    # data = yf.download(tickers, start=dater, end=(date.fromisoformat(dater)+timedelta(days=1)).isoformat(), interval="1h")
    # with open("testText.txt", "w") as f:
    #     f.write(data.to_string(index=False))
    # tickers = get_tickers()