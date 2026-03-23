import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
DB_NAME = "stockpulse"
DB_USER = os.getenv("DB_USER", "postgres")
DB_HOST = "localhost"
DB_PORT = "5432"

def get_engine():
    if DATABASE_URL:
        return create_engine(DATABASE_URL)
    return create_engine(
        f"postgresql://{DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

def create_tables():
    engine = get_engine()
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS stock_prices (
                id SERIAL PRIMARY KEY,
                ticker VARCHAR(10) NOT NULL,
                date DATE NOT NULL,
                open FLOAT,
                high FLOAT,
                low FLOAT,
                close FLOAT,
                volume BIGINT,
                created_at TIMESTAMP DEFAULT NOW(),
                UNIQUE(ticker, date)
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS news_headlines (
                id SERIAL PRIMARY KEY,
                ticker VARCHAR(10) NOT NULL,
                headline TEXT NOT NULL,
                source VARCHAR(100),
                published_at TIMESTAMP,
                sentiment_score FLOAT,
                sentiment_label VARCHAR(10),
                created_at TIMESTAMP DEFAULT NOW()
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS predictions (
                id SERIAL PRIMARY KEY,
                ticker VARCHAR(10) NOT NULL,
                prediction_date DATE NOT NULL,
                predicted_direction VARCHAR(5),
                confidence FLOAT,
                created_at TIMESTAMP DEFAULT NOW(),
                UNIQUE(ticker, prediction_date)
            )
        """))
        conn.commit()
        print("Tables created!")

if __name__ == "__main__":
    create_tables()