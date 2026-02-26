"""Pytest configuration and fixtures for Stock Agent tests."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture
def mock_yfinance_ticker():
    """Create a mock yfinance Ticker object."""
    mock_ticker = MagicMock()
    mock_ticker.info = {
        "symbol": "AAPL",
        "shortName": "Apple Inc.",
        "longName": "Apple Inc.",
        "sector": "Technology",
        "industry": "Consumer Electronics",
        "currentPrice": 175.50,
        "previousClose": 174.00,
        "regularMarketPrice": 175.50,
        "dayHigh": 176.00,
        "dayLow": 173.50,
        "volume": 50000000,
        "averageVolume": 45000000,
        "marketCap": 2800000000000,
        "fiftyTwoWeekHigh": 200.00,
        "fiftyTwoWeekLow": 150.00,
        "currency": "USD",
        "trailingPE": 28.5,
        "forwardPE": 25.0,
        "pegRatio": 1.5,
        "priceToBook": 45.0,
        "priceToSalesTrailing12Months": 7.5,
        "enterpriseValue": 2900000000000,
        "trailingEps": 6.15,
        "forwardEps": 7.00,
        "profitMargins": 0.25,
        "operatingMargins": 0.30,
        "grossMargins": 0.43,
        "returnOnEquity": 0.85,
        "returnOnAssets": 0.25,
        "dividendYield": 0.005,
        "dividendRate": 0.96,
        "payoutRatio": 0.15,
        "revenueGrowth": 0.08,
        "earningsGrowth": 0.10,
        "totalDebt": 110000000000,
        "totalCash": 65000000000,
        "debtToEquity": 150,
        "currentRatio": 1.0,
        "quickRatio": 0.95,
        "freeCashflow": 90000000000,
        "beta": 1.2,
        "sharesOutstanding": 16000000000,
        "recommendationKey": "buy",
        "recommendationMean": 1.8,
        "numberOfAnalystOpinions": 40,
        "targetHighPrice": 220.00,
        "targetLowPrice": 160.00,
        "targetMeanPrice": 195.00,
        "targetMedianPrice": 195.00,
    }
    return mock_ticker


@pytest.fixture
def mock_yfinance_history():
    """Create mock historical data."""
    import pandas as pd
    from datetime import datetime, timedelta

    dates = pd.date_range(end=datetime.now(), periods=30, freq="D")
    data = {
        "Open": [170 + i * 0.2 for i in range(30)],
        "High": [172 + i * 0.2 for i in range(30)],
        "Low": [168 + i * 0.2 for i in range(30)],
        "Close": [171 + i * 0.2 for i in range(30)],
        "Volume": [50000000 for _ in range(30)],
    }
    return pd.DataFrame(data, index=dates)


@pytest.fixture
def sample_stock_symbols():
    """Return a list of sample stock symbols for testing."""
    return ["AAPL", "MSFT", "GOOGL", "AMZN", "META"]


@pytest.fixture
def mock_bedrock_client():
    """Create a mock Bedrock client."""
    mock_client = MagicMock()
    mock_client.invoke_model.return_value = {
        "body": MagicMock(read=lambda: b'{"completion": "Test response"}')
    }
    return mock_client
