tickers = []
with open("stocks.txt", "r", encoding="utf-8") as file:
    for line in file:
        # .strip() removes trailing newlines (\n) and whitespace
        tickers.append(line.strip())


print(tickers)