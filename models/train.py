import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import pickle
import os
from models.sentiment import build_features
from dotenv import load_dotenv

load_dotenv()

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

def train_model(ticker):
    print(f"\nTraining model for {ticker}...")
    df = build_features(ticker)

    if len(df) < 30:
        print(f"Not enough data for {ticker}, skipping.")
        return

    X = df[FEATURES]
    y = df["target"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=False
    )

    model = XGBClassifier(
        n_estimators=100,
        max_depth=3,
        learning_rate=0.1,
        random_state=42,
        eval_metric="logloss"
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Accuracy for {ticker}: {accuracy:.2%}")
    print(classification_report(y_test, y_pred, target_names=["Down", "Up"]))

    os.makedirs("models/saved", exist_ok=True)
    with open(f"models/saved/{ticker}_model.pkl", "wb") as f:
        pickle.dump(model, f)
    print(f"Model saved for {ticker}")

def train_all():
    for ticker in TICKERS:
        train_model(ticker)

if __name__ == "__main__":
    train_all()