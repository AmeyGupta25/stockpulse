import yfinance as yf
import pandas as pd
from sqlalchemy import text
from data.database import get_engine
from dotenv import load_dotenv

load_dotenv()

TICKERS = ["AAPL", "TSLA", "NVDA", "MSFT", "GOOGL"]

def fetch_and_store_prices(ticker, period="6mo"):
    print(f"Fetching prices for {ticker}...")
    stock = yf.Ticker(ticker)
    df = stock.history(period=period)
    
    if df.empty:
        print(f"No data found for {ticker}")
        return
    
    df = df.reset_index()
    df = df[["Date", "Open", "High", "Low", "Close", "Volume"]]
    df.columns = ["date", "open", "high", "low", "close", "volume"]
    df["ticker"] = ticker
    df["date"] = pd.to_datetime(df["date"]).dt.date

    engine = get_engine()
    with engine.connect() as conn:
        for _, row in df.iterrows():
            conn.execute(text("""
                INSERT INTO stock_prices (ticker, date, open, high, low, close, volume)
                VALUES (:ticker, :date, :open, :high, :low, :close, :volume)
                ON CONFLICT (ticker, date) DO NOTHING
            """), {
                "ticker": row["ticker"],
                "date": row["date"],
                "open": row["open"],
                "high": row["high"],
                "low": row["low"],
                "close": row["close"],
                "volume": int(row["volume"])
            })
        conn.commit()
    print(f"Stored {len(df)} rows for {ticker}")

if __name__ == "__main__":
    for ticker in TICKERS:
        fetch_and_store_prices(ticker)