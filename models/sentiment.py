import pandas as pd
from sqlalchemy import text
from data.database import get_engine

def get_daily_sentiment(ticker):
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT 
                DATE(published_at) as date,
                AVG(sentiment_score) as avg_sentiment,
                COUNT(*) as headline_count,
                SUM(CASE WHEN sentiment_label = 'positive' THEN 1 ELSE 0 END) as positive_count,
                SUM(CASE WHEN sentiment_label = 'negative' THEN 1 ELSE 0 END) as negative_count
            FROM news_headlines
            WHERE ticker = :ticker
            GROUP BY DATE(published_at)
            ORDER BY date
        """), {"ticker": ticker})
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
    return df

def get_price_data(ticker):
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT date, open, high, low, close, volume
            FROM stock_prices
            WHERE ticker = :ticker
            ORDER BY date
        """), {"ticker": ticker})
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
    return df

def build_features(ticker):
    prices = get_price_data(ticker)
    sentiment = get_daily_sentiment(ticker)

    prices["date"] = pd.to_datetime(prices["date"])
    sentiment["date"] = pd.to_datetime(sentiment["date"])

    df = prices.copy()

    df["price_change"] = df["close"].pct_change()
    df["price_momentum_3d"] = df["close"].pct_change(3)
    df["price_momentum_5d"] = df["close"].pct_change(5)
    df["volume_change"] = df["volume"].pct_change()
    df["high_low_range"] = (df["high"] - df["low"]) / df["close"]

    df = df.merge(sentiment, on="date", how="left")
    df["avg_sentiment"] = df["avg_sentiment"].fillna(0)
    df["headline_count"] = df["headline_count"].fillna(0)
    df["positive_count"] = df["positive_count"].fillna(0)
    df["negative_count"] = df["negative_count"].fillna(0)

    df["target"] = (df["close"].shift(-1) > df["close"]).astype(int)

    df = df.dropna()
    return df

if __name__ == "__main__":
    df = build_features("AAPL")
    print(df[["date", "close", "avg_sentiment", "target"]].tail(10))
    print(f"\nDataset shape: {df.shape}")