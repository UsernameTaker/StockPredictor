import yfinance as yf
from datetime import date, timedelta
from stockModel import get_tickers
if __name__ == "__main__":
    dater = "2026-06-11"
    ticker = yf.Ticker("AADX")
    data = yf.download("SDOT", start=dater, end=(date.fromisoformat(dater)+timedelta(days=1)).isoformat(), interval="1m")
    print(data)
    # tickers = get_tickers()