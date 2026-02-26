"""Tests for Stock Agent tools."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestSectorTools:
    """Tests for sector_tools module."""

    def test_get_stocks_by_sector_valid_sector(self, mock_yfinance_ticker):
        """Test getting stocks for a valid sector."""
        from stock_agent.tools.sector_tools import get_stocks_by_sector

        with patch("stock_agent.tools.sector_tools.yf.Ticker") as mock_ticker_class:
            mock_ticker_class.return_value = mock_yfinance_ticker

            result = get_stocks_by_sector(sector="technology", limit=5)

            assert "sector" in result
            assert "stocks" in result
            assert result["sector"] == "technology"
            assert len(result["stocks"]) <= 5

    def test_get_stocks_by_sector_invalid_sector(self):
        """Test getting stocks for an invalid sector."""
        from stock_agent.tools.sector_tools import get_stocks_by_sector

        result = get_stocks_by_sector(sector="invalid_sector", limit=5)

        assert "error" in result
        assert "available_sectors" in result

    def test_list_industries_in_sector_valid(self):
        """Test listing industries for a valid sector."""
        from stock_agent.tools.sector_tools import list_industries_in_sector

        result = list_industries_in_sector(sector="technology")

        assert "sector" in result
        assert "industries" in result
        assert "count" in result
        assert len(result["industries"]) > 0

    def test_list_industries_in_sector_invalid(self):
        """Test listing industries for an invalid sector."""
        from stock_agent.tools.sector_tools import list_industries_in_sector

        result = list_industries_in_sector(sector="invalid")

        assert "error" in result
        assert "available_sectors" in result


class TestStockTools:
    """Tests for stock_tools module."""

    def test_get_stock_quote(self, mock_yfinance_ticker):
        """Test getting a stock quote."""
        from stock_agent.tools.stock_tools import get_stock_quote

        with patch("stock_agent.tools.stock_tools.yf.Ticker") as mock_ticker_class:
            mock_ticker_class.return_value = mock_yfinance_ticker

            result = get_stock_quote(symbol="AAPL")

            assert result["symbol"] == "AAPL"
            assert "current_price" in result
            assert "market_cap" in result
            assert result["current_price"] == 175.50

    def test_get_stock_quote_invalid_symbol(self):
        """Test getting a quote for an invalid symbol."""
        from stock_agent.tools.stock_tools import get_stock_quote

        mock_ticker = MagicMock()
        mock_ticker.info = {}

        with patch("stock_agent.tools.stock_tools.yf.Ticker") as mock_ticker_class:
            mock_ticker_class.return_value = mock_ticker

            result = get_stock_quote(symbol="INVALID123")

            assert "error" in result

    def test_get_stock_metrics(self, mock_yfinance_ticker):
        """Test getting stock metrics."""
        from stock_agent.tools.stock_tools import get_stock_metrics

        with patch("stock_agent.tools.stock_tools.yf.Ticker") as mock_ticker_class:
            mock_ticker_class.return_value = mock_yfinance_ticker

            result = get_stock_metrics(symbol="AAPL")

            assert result["symbol"] == "AAPL"
            assert "pe_ratio" in result
            assert "eps" in result
            assert "dividend_yield" in result
            assert result["pe_ratio"] == 28.5

    def test_compare_stocks(self, mock_yfinance_ticker):
        """Test comparing multiple stocks."""
        from stock_agent.tools.stock_tools import compare_stocks

        with patch("stock_agent.tools.stock_tools.yf.Ticker") as mock_ticker_class:
            mock_ticker_class.return_value = mock_yfinance_ticker

            result = compare_stocks(symbols=["AAPL", "MSFT"])

            assert "stocks" in result
            assert "count" in result

    def test_compare_stocks_empty_list(self):
        """Test comparing with empty list."""
        from stock_agent.tools.stock_tools import compare_stocks

        result = compare_stocks(symbols=[])

        assert "error" in result

    def test_compare_stocks_too_many(self):
        """Test comparing too many stocks."""
        from stock_agent.tools.stock_tools import compare_stocks

        symbols = [f"SYM{i}" for i in range(15)]
        result = compare_stocks(symbols=symbols)

        assert "error" in result

    def test_get_stock_history(self, mock_yfinance_ticker, mock_yfinance_history):
        """Test getting stock history."""
        from stock_agent.tools.stock_tools import get_stock_history

        mock_yfinance_ticker.history.return_value = mock_yfinance_history

        with patch("stock_agent.tools.stock_tools.yf.Ticker") as mock_ticker_class:
            mock_ticker_class.return_value = mock_yfinance_ticker

            result = get_stock_history(symbol="AAPL", period="1mo")

            assert result["symbol"] == "AAPL"
            assert "data_points" in result
            assert "recent_data" in result

    def test_get_stock_history_invalid_period(self):
        """Test getting history with invalid period."""
        from stock_agent.tools.stock_tools import get_stock_history

        result = get_stock_history(symbol="AAPL", period="invalid")

        assert "error" in result
        assert "valid_periods" in result


class TestAnalysisTools:
    """Tests for analysis_tools module."""

    def test_get_analyst_recommendations(self, mock_yfinance_ticker):
        """Test getting analyst recommendations."""
        from stock_agent.tools.analysis_tools import get_analyst_recommendations

        mock_yfinance_ticker.recommendations = None

        with patch("stock_agent.tools.analysis_tools.yf.Ticker") as mock_ticker_class:
            mock_ticker_class.return_value = mock_yfinance_ticker

            result = get_analyst_recommendations(symbol="AAPL")

            assert result["symbol"] == "AAPL"
            assert "recommendation" in result
            assert "target_mean" in result

    def test_get_stock_news(self, mock_yfinance_ticker):
        """Test getting stock news."""
        from stock_agent.tools.analysis_tools import get_stock_news

        mock_yfinance_ticker.news = [
            {
                "title": "Test News Article",
                "publisher": "Test Publisher",
                "link": "https://example.com/news",
                "type": "article",
                "providerPublishTime": 1700000000,
            }
        ]

        with patch("stock_agent.tools.analysis_tools.yf.Ticker") as mock_ticker_class:
            mock_ticker_class.return_value = mock_yfinance_ticker

            result = get_stock_news(symbol="AAPL", limit=5)

            assert result["symbol"] == "AAPL"
            assert "news" in result
            assert len(result["news"]) > 0

    def test_get_stock_news_no_news(self, mock_yfinance_ticker):
        """Test getting news when none available."""
        from stock_agent.tools.analysis_tools import get_stock_news

        mock_yfinance_ticker.news = []

        with patch("stock_agent.tools.analysis_tools.yf.Ticker") as mock_ticker_class:
            mock_ticker_class.return_value = mock_yfinance_ticker

            result = get_stock_news(symbol="AAPL", limit=5)

            assert result["count"] == 0
            assert "message" in result

    def test_analyze_stock_value(self, mock_yfinance_ticker):
        """Test stock value analysis."""
        from stock_agent.tools.analysis_tools import analyze_stock_value

        with patch("stock_agent.tools.analysis_tools.yf.Ticker") as mock_ticker_class:
            mock_ticker_class.return_value = mock_yfinance_ticker

            result = analyze_stock_value(symbol="AAPL")

            assert result["symbol"] == "AAPL"
            assert "overall_signal" in result
            assert result["overall_signal"] in ["BULLISH", "BEARISH", "NEUTRAL"]
            assert "positive_factors" in result
            assert "negative_factors" in result
            assert "disclaimer" in result


class TestConfig:
    """Tests for config module."""

    def test_agent_config_defaults(self):
        """Test AgentConfig default values."""
        from stock_agent.config import AgentConfig

        config = AgentConfig()

        assert config.aws_region == "us-east-1"
        assert "nova" in config.model_id.lower()
        assert config.max_tokens > 0
        assert 0 <= config.temperature <= 1

    def test_agent_config_system_prompt(self):
        """Test that system prompt is defined."""
        from stock_agent.config import AgentConfig

        config = AgentConfig()

        assert config.system_prompt is not None
        assert len(config.system_prompt) > 100
        assert "stock" in config.system_prompt.lower()
