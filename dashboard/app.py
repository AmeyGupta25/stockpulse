import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests

API_BASE = "http://localhost:8000"
TICKERS = ["AAPL", "TSLA", "NVDA", "MSFT", "GOOGL", "AMZN", "META", "JPM", "NFLX", "AMD"]

BG = "#F8F9FA"
CARD = "#FFFFFF"
GREEN = "#00897B"
RED = "#E53935"
BLUE = "#1565C0"
BORDER = "#E0E0E0"
TEXT = "#1A1A2E"
SUBTEXT = "#6B7280"
ACCENT_BG_GREEN = "rgba(0,137,123,0.08)"
ACCENT_BG_RED = "rgba(229,57,53,0.08)"

def fetch_prices(ticker):
    r = requests.get(f"{API_BASE}/prices/{ticker}?limit=60")
    data = r.json()["prices"]
    dates = [d["date"] for d in reversed(data)]
    closes = [d["close"] for d in reversed(data)]
    volumes = [d["volume"] for d in reversed(data)]
    highs = [d["high"] for d in reversed(data)]
    lows = [d["low"] for d in reversed(data)]
    return dates, closes, volumes, highs, lows

def fetch_sentiment(ticker):
    r = requests.get(f"{API_BASE}/sentiment/{ticker}")
    data = r.json()
    return data["average_sentiment"], data["headlines"]

def fetch_prediction(ticker):
    r = requests.get(f"{API_BASE}/prediction/{ticker}")
    return r.json()

def build_dashboard(ticker="AAPL"):
    dates, closes, volumes, highs, lows = fetch_prices(ticker)
    avg_sentiment, headlines = fetch_sentiment(ticker)
    prediction = fetch_prediction(ticker)

    price_up = closes[-1] >= closes[0]
    pred_up = prediction["prediction"] == "Up"
    price_color = GREEN if price_up else RED
    pred_color = GREEN if pred_up else RED

    price_change = closes[-1] - closes[0]
    price_change_pct = (price_change / closes[0]) * 100
    sent_label = "Bullish" if avg_sentiment > 0.05 else "Bearish" if avg_sentiment < -0.05 else "Neutral"
    sent_color = GREEN if avg_sentiment > 0.05 else RED if avg_sentiment < -0.05 else SUBTEXT

    fig = make_subplots(
        rows=3, cols=3,
        specs=[
            [{"type": "scatter", "colspan": 2}, None, {"type": "indicator"}],
            [{"type": "bar", "colspan": 2}, None, {"type": "indicator"}],
            [{"type": "table", "colspan": 3}, None, None]
        ],
        vertical_spacing=0.07,
        horizontal_spacing=0.06,
        row_heights=[0.38, 0.22, 0.40]
    )

    fig.add_trace(
        go.Scatter(
            x=dates, y=closes,
            mode="lines",
            line=dict(color=price_color, width=2.5),
            fill="tozeroy",
            fillcolor=ACCENT_BG_GREEN if price_up else ACCENT_BG_RED,
            name="Close Price",
            hovertemplate="<b>%{x}</b><br>$%{y:.2f}<extra></extra>"
        ),
        row=1, col=1
    )

    vol_colors = [GREEN if closes[i] >= closes[i-1] else RED for i in range(1, len(closes))]
    vol_colors.insert(0, GREEN)

    fig.add_trace(
        go.Bar(
            x=dates,
            y=volumes,
            marker_color=vol_colors,
            marker_line_width=0,
            opacity=0.5,
            name="Volume",
            hovertemplate="<b>%{x}</b><br>%{y:,.0f}<extra></extra>"
        ),
        row=2, col=1
    )

    fig.add_trace(
        go.Indicator(
            mode="number+delta",
            value=closes[-1],
            delta={
                "reference": closes[0],
                "valueformat": ".2f",
                "increasing": {"color": GREEN},
                "decreasing": {"color": RED},
                "prefix": "$"
            },
            number={
                "prefix": "$",
                "font": {"size": 40, "color": TEXT},
                "valueformat": ".2f"
            },
            title={
                "text": f"<span style='font-size:13px;color:{SUBTEXT}'>Latest Close</span><br><span style='font-size:14px;color:{price_color}'>{'▲' if price_up else '▼'} {abs(price_change_pct):.2f}% over 60 days</span>"
            }
        ),
        row=1, col=3
    )

    conf_pct = prediction["confidence"] * 100
    fig.add_trace(
        go.Indicator(
            mode="number",
            value=conf_pct,
            number={
                "suffix": "%",
                "font": {"size": 40, "color": pred_color},
                "valueformat": ".1f"
            },
            title={
                "text": f"<span style='font-size:13px;color:{SUBTEXT}'>ML Prediction</span><br><span style='font-size:16px;font-weight:bold;color:{pred_color}'>{'▲' if pred_up else '▼'} {prediction['prediction']} &nbsp;</span><br><span style='font-size:12px;color:{sent_color}'>Sentiment: {sent_label} ({avg_sentiment:+.3f})</span>"
            }
        ),
        row=2, col=3
    )

    headline_texts = [
        h["headline"][:75] + "..." if len(h["headline"]) > 75 else h["headline"]
        for h in headlines[:8]
    ]
    sentiment_labels = [h["sentiment_label"].capitalize() for h in headlines[:8]]
    sentiment_scores = [f"{h['sentiment_score']:+.3f}" for h in headlines[:8]]
    sources = [h.get("source", "Yahoo Finance") for h in headlines[:8]]

    row_colors = []
    for h in headlines[:8]:
        if h["sentiment_label"] == "positive":
            row_colors.append("rgba(0,137,123,0.07)")
        elif h["sentiment_label"] == "negative":
            row_colors.append("rgba(229,57,53,0.07)")
        else:
            row_colors.append(CARD)

    score_font_colors = [
        GREEN if float(s) >= 0 else RED for s in sentiment_scores
    ]

    fig.add_trace(
        go.Table(
            columnwidth=[420, 140, 110, 90],
            header=dict(
                values=["<b>Headline</b>", "<b>Source</b>", "<b>Sentiment</b>", "<b>Score</b>"],
                fill_color=BLUE,
                font=dict(color="white", size=12),
                align=["left", "left", "center", "center"],
                height=36,
                line=dict(color=CARD, width=1)
            ),
            cells=dict(
                values=[headline_texts, sources, sentiment_labels, sentiment_scores],
                fill_color=[row_colors, row_colors, row_colors, row_colors],
                font=dict(
                    color=[
                        [TEXT] * 8,
                        [SUBTEXT] * 8,
                        [GREEN if s == "Positive" else RED if s == "Negative" else SUBTEXT for s in sentiment_labels],
                        score_font_colors
                    ],
                    size=12
                ),
                align=["left", "left", "center", "center"],
                height=30,
                line=dict(color=BORDER, width=1)
            )
        ),
        row=3, col=1
    )

    fig.update_layout(
        title=dict(
            text=f"<b style='color:{TEXT};font-size:22px'>{ticker}</b><span style='color:{SUBTEXT};font-size:16px'> / StockPulse Analytics</span>",
            x=0.02,
            font=dict(size=22)
        ),
        height=860,
        showlegend=False,
        paper_bgcolor=BG,
        plot_bgcolor=CARD,
        font=dict(color=TEXT, family="Inter, Arial, sans-serif"),
        margin=dict(l=40, r=40, t=75, b=30)
    )

    fig.update_xaxes(
        gridcolor=BORDER,
        linecolor=BORDER,
        tickfont=dict(color=SUBTEXT, size=10),
        showgrid=True,
        zeroline=False
    )
    fig.update_yaxes(
        gridcolor=BORDER,
        linecolor=BORDER,
        tickfont=dict(color=SUBTEXT, size=10),
        showgrid=True,
        zeroline=False
    )

    fig.write_html(f"dashboard/{ticker}_dashboard.html")
    print(f"Saved: dashboard/{ticker}_dashboard.html")

if __name__ == "__main__":
    for ticker in TICKERS:
        build_dashboard(ticker)
    print("\nAll dashboards generated!")