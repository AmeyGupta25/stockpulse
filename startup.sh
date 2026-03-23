#!/bin/bash
echo "Running startup script..."
python -m data.database
python -m data.stock_scraper
python -m data.news_scraper
python -m models.train
echo "Startup complete!"
uvicorn api.main:app --host 0.0.0.0 --port $PORT