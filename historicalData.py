from stockModel import get_tickers
import os
import pandas as pd
import yfinance as yf
print("Hello world!")

if __name__ == "__main__":
    DATA_DIR = "./data/5 min/us/" 
    TARGET_DATE = "2026-05-26" 

    try:
        all_losses = pd.read_csv("historicalDataTickers.txt", sep="\t")
    except Exception as e:
        print(f"Error reading historicalDataTickers.txt: {e}")
        all_losses = pd.DataFrame()

    daily_losses = []

    for root, dirs, files in os.walk(DATA_DIR):
        print("Processing directory: " + root)
        for file in files:
            if file.endswith(".txt"):
                file_path = os.path.join(root, file)
                ticker = file[:-7].upper()  # Remove the ".us.txt" extension
                print("Processing file: " + file)
            try:
                data = pd.read_csv(file_path, index_col=0, parse_dates=['<DATE>'])
                data.columns = [col.replace('<', '').replace('>', '') for col in data.columns]
                day_data = data[TARGET_DATE.replace('-', '') == data['DATE']]
                if not day_data.empty and day_data is not None:
                    close = day_data.loc[day_data['TIME'] == 215500, 'CLOSE'].item()
                    open = day_data.loc[day_data['TIME'] == 153000, 'OPEN'].item()
                    if close > 5 and ((close - open) / open) < -0.05:
                        if root.split("/")[-1] != "nysemkt stocks":
                         stock_exchange = root.split("/")[-2]
                        else:
                            stock_exchange = root.split("/")[-1]
                        daily_losses.append(
                            {'Date': TARGET_DATE,
                                'Ticker': ticker,
                             'Change %': round(((close - open) / open) * 100, 3),
                             'Stock Exchange': stock_exchange
                            })

            except Exception as e:
                print(f"Error reading {file}: {e}")
                continue
    print("Done getting top daily losses! Found: " + str(len(daily_losses)))
    top_daily_losses = pd.DataFrame(daily_losses).sort_values(by='Change %', ascending=True)
    for t in top_daily_losses['Ticker']:
        try:
            ticker = yf.Ticker(t)
            info = ticker.info
            quoteType = info.get('quoteType', '')
            if(quoteType != 'EQUITY'):
                top_daily_losses = top_daily_losses[top_daily_losses['Ticker'] != t]
        except Exception as e:
            top_daily_losses = top_daily_losses[top_daily_losses['Ticker'] != t]
            print(f"Error fetching data for {t}: {e}")
    #print(top_daily_losses)
    if not all_losses.empty:
        if not TARGET_DATE in all_losses['Date'].values:
            all_losses = pd.concat([all_losses, top_daily_losses], ignore_index=True)
        else:
            print("This date is already in the data.")
    all_losses.to_csv("historicalDataTickers.txt", sep="\t", index=False)
