import yfinance as yf
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sqlalchemy import text
from data.database import get_engine
from dotenv import load_dotenv
import datetime

load_dotenv()

TICKERS = ["AAPL", "TSLA", "NVDA", "MSFT", "GOOGL", "AMZN", "META", "JPM", "NFLX", "AMD"]
analyzer = SentimentIntensityAnalyzer()

def fetch_and_store_news(ticker):
    print(f"Fetching news for {ticker}...")
    stock = yf.Ticker(ticker)
    news = stock.news

    if not news:
        print(f"No news found for {ticker}")
        return

    engine = get_engine()
    stored = 0
    with engine.connect() as conn:
        for item in news:
            try:
                content = item.get("content", {})
                headline = content.get("title", "")
                source = content.get("provider", {}).get("displayName", "Yahoo Finance")
                pub_date = content.get("pubDate", "")

                if not headline:
                    continue

                scores = analyzer.polarity_scores(headline)
                compound = scores["compound"]
                if compound >= 0.05:
                    label = "positive"
                elif compound <= -0.05:
                    label = "negative"
                else:
                    label = "neutral"

                if pub_date:
                    published_at = datetime.datetime.fromisoformat(
                        pub_date.replace("Z", "+00:00")
                    )
                else:
                    published_at = datetime.datetime.now()

                conn.execute(text("""
                    INSERT INTO news_headlines 
                        (ticker, headline, source, published_at, sentiment_score, sentiment_label)
                    VALUES 
                        (:ticker, :headline, :source, :published_at, :sentiment_score, :sentiment_label)
                """), {
                    "ticker": ticker,
                    "headline": headline,
                    "source": source,
                    "published_at": published_at,
                    "sentiment_score": compound,
                    "sentiment_label": label
                })
                stored += 1
            except Exception as e:
                print(f"Skipping item: {e}")
                continue

        conn.commit()
    print(f"Stored {stored} headlines for {ticker}")

if __name__ == "__main__":
    for ticker in TICKERS:
        fetch_and_store_news(ticker)