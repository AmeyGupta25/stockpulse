from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from data.database import get_engine
import pickle
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="StockPulse API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

TICKERS = ["AAPL", "TSLA", "NVDA", "MSFT", "GOOGL", "AMZN", "META", "JPM", "NFLX", "AMD"]

FEATURES = [
    "price_change",
    "price_momentum_3d",
    "price_momentum_5d",
    "volume_change",
    "high_low_range",
    "avg_sentiment",
    "headline_count",
    "positive_count",
    "negative_count"
]

def load_model(ticker):
    path = f"models/saved/{ticker}_model.pkl"
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return pickle.load(f)

@app.get("/")
def root():
    return {"message": "StockPulse API is running"}

@app.get("/tickers")
def get_tickers():
    return {"tickers": TICKERS}

@app.get("/prices/{ticker}")
def get_prices(ticker: str, limit: int = 30):
    ticker = ticker.upper()
    if ticker not in TICKERS:
        raise HTTPException(status_code=404, detail="Ticker not found")
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT date, open, high, low, close, volume
            FROM stock_prices
            WHERE ticker = :ticker
            ORDER BY date DESC
            LIMIT :limit
        """), {"ticker": ticker, "limit": limit})
        rows = [dict(row._mapping) for row in result.fetchall()]
    return {"ticker": ticker, "prices": rows}

@app.get("/sentiment/{ticker}")
def get_sentiment(ticker: str):
    ticker = ticker.upper()
    if ticker not in TICKERS:
        raise HTTPException(status_code=404, detail="Ticker not found")
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT headline, source, published_at, sentiment_score, sentiment_label
            FROM news_headlines
            WHERE ticker = :ticker
            ORDER BY published_at DESC
            LIMIT 20
        """), {"ticker": ticker})
        rows = [dict(row._mapping) for row in result.fetchall()]
    avg = sum(r["sentiment_score"] for r in rows) / len(rows) if rows else 0
    return {
        "ticker": ticker,
        "average_sentiment": round(avg, 4),
        "headlines": rows
    }

@app.get("/prediction/{ticker}")
def get_prediction(ticker: str):
    ticker = ticker.upper()
    if ticker not in TICKERS:
        raise HTTPException(status_code=404, detail="Ticker not found")

    model = load_model(ticker)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found for ticker")

    engine = get_engine()
    with engine.connect() as conn:
        prices = conn.execute(text("""
            SELECT date, open, high, low, close, volume
            FROM stock_prices
            WHERE ticker = :ticker
            ORDER BY date DESC
            LIMIT 10
        """), {"ticker": ticker})
        price_df = pd.DataFrame(prices.fetchall(), columns=prices.keys())

        sentiment = conn.execute(text("""
            SELECT AVG(sentiment_score) as avg_sentiment,
                   COUNT(*) as headline_count,
                   SUM(CASE WHEN sentiment_label = 'positive' THEN 1 ELSE 0 END) as positive_count,
                   SUM(CASE WHEN sentiment_label = 'negative' THEN 1 ELSE 0 END) as negative_count
            FROM news_headlines
            WHERE ticker = :ticker
        """), {"ticker": ticker})
        sent_row = sentiment.fetchone()

    price_df = price_df.sort_values("date")
    price_df["price_change"] = price_df["close"].pct_change()
    price_df["price_momentum_3d"] = price_df["close"].pct_change(3)
    price_df["price_momentum_5d"] = price_df["close"].pct_change(5)
    price_df["volume_change"] = price_df["volume"].pct_change()
    price_df["high_low_range"] = (price_df["high"] - price_df["low"]) / price_df["close"]

    latest = price_df.iloc[-1].copy()
    latest["avg_sentiment"] = float(sent_row[0] or 0)
    latest["headline_count"] = float(sent_row[1] or 0)
    latest["positive_count"] = float(sent_row[2] or 0)
    latest["negative_count"] = float(sent_row[3] or 0)

    X = pd.DataFrame([latest[FEATURES]])
    prediction = model.predict(X)[0]
    confidence = model.predict_proba(X)[0][prediction]

    return {
        "ticker": ticker,
        "prediction": "Up" if prediction == 1 else "Down",
        "confidence": round(float(confidence), 4),
        "latest_close": round(float(latest["close"]), 2)
    }