import yfinance as yf
if __name__ == "__main__":
    ticker = yf.Ticker("AADX")
    data = yf.download("SDOT", start="2026-05-26", end="2026-05-27", interval="1m")
    print(data)