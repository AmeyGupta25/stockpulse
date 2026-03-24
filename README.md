# StockPulse Analytics

A full-stack data engineering and machine learning project that tracks real-time stock prices, analyzes news sentiment, and predicts next-day price direction using XGBoost.

## Live Links
- **Live Dashboard:** https://ameygupta25.github.io/stockpulse/index.html
- **Live API:** https://stockpulse-api-rt7t.onrender.com
- **API Docs:** https://stockpulse-api-rt7t.onrender.com/docs

> Note: The API is hosted on Render's free tier and may take up to 50 seconds to wake up after inactivity.

## Demo
<img width="1470" height="838" alt="StockPulse Dashboard" src="https://github.com/user-attachments/assets/2d756ff7-efaa-4966-8539-5f50880adb17" />

## Tech Stack
- **Data Ingestion:** yfinance, Yahoo Finance News
- **Sentiment Analysis:** VADER (Valence Aware Dictionary and sEntiment Reasoner)
- **ML Model:** XGBoost classifier with feature engineering
- **Backend:** FastAPI with auto-generated API docs
- **Database:** PostgreSQL with SQLAlchemy ORM
- **Frontend:** Vanilla JS + Plotly.js (live API calls, no page refresh needed)
- **Deployment:** Render (API + database), GitHub Pages (frontend)

## Architecture
```
yfinance / Yahoo Finance News
        │
        ▼
  Data Ingestion Scripts
  (stock_scraper.py / news_scraper.py)
        │
        ▼
  PostgreSQL Database
  ┌─────────────────────┐
  │  stock_prices       │
  │  news_headlines     │
  │  predictions        │
  └─────────────────────┘
        │
        ▼
  Feature Engineering + Sentiment Scoring
  (sentiment.py)
        │
        ▼
  XGBoost Model Training
  (train.py)
        │
        ▼
  FastAPI REST API
  /prices /sentiment /prediction
        │
        ▼
  Live Interactive Dashboard (GitHub Pages)
  Fetches from API in real time on every visit
```

## Features
- Tracks 10 tickers: AAPL, TSLA, NVDA, MSFT, GOOGL, AMZN, META, JPM, NFLX, AMD
- Pulls and stores 6 months of historical OHLCV price data
- Scores news headlines with VADER sentiment analysis
- Engineers 9 features combining price momentum and sentiment signals
- Trains an XGBoost classifier per ticker to predict next-day price direction
- Serves live predictions through a REST API with auto-generated docs
- Renders a live interactive dashboard that fetches real-time data from the API on every visit

## API Endpoints
| Endpoint | Description |
|---|---|
| `GET /prices/{ticker}` | Last N days of OHLCV price data |
| `GET /sentiment/{ticker}` | Latest headlines with sentiment scores |
| `GET /prediction/{ticker}` | ML model prediction + confidence |
| `GET /docs` | Interactive API documentation |

## Model Performance
| Ticker | Accuracy |
|---|---|
| AAPL | 45.8% |
| TSLA | 50.0% |
| NVDA | 41.7% |
| MSFT | 41.7% |
| GOOGL | 45.8% |
| AMZN | 50.0% |
| META | 45.8% |
| JPM | 54.2% |
| NFLX | 54.2% |
| AMD | 50.0% |

> Note: Stock price prediction is an inherently noisy problem. These results are expected for a model trained on 6 months of data with limited sentiment overlap. Model performance improves as more sentiment data accumulates over time. This project is a proof of concept demonstrating end-to-end ML pipeline architecture, not a trading system.

## Setup

### Prerequisites
- Python 3.11+
- PostgreSQL 15
- Homebrew (Mac)

### Installation
```bash
git clone https://github.com/AmeyGupta25/stockpulse.git
cd stockpulse
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Environment Variables
Create a `.env` file:
```
ALPHA_VANTAGE_KEY=your_key_here
DB_USER=your_postgres_username
```

### Run
```bash
# Ingest data
python -m data.stock_scraper
python -m data.news_scraper

# Train models
python -m models.train

# Start API
uvicorn api.main:app --reload
```

## Project Structure
```
stockpulse/
├── data/
│   ├── database.py        # DB connection + table setup
│   ├── stock_scraper.py   # Price ingestion via yfinance
│   └── news_scraper.py    # News + sentiment ingestion
├── models/
│   ├── sentiment.py       # Feature engineering
│   ├── train.py           # XGBoost training + evaluation
│   └── saved/             # Trained model artifacts
├── api/
│   └── main.py            # FastAPI REST endpoints
├── dashboard/
│   └── app.py             # Local Plotly dashboard generation
└── .env                   # API keys (not committed)
```