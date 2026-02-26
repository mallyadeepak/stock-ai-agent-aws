"""Stock data tools for quotes, metrics, and historical data."""

import logging
from typing import Any

import yfinance as yf
from strands import tool

logger = logging.getLogger(__name__)


def _format_large_number(num: float | None) -> str | None:
    """Format large numbers for readability."""
    if num is None:
        return None
    if num >= 1_000_000_000_000:
        return f"${num / 1_000_000_000_000:.2f}T"
    if num >= 1_000_000_000:
        return f"${num / 1_000_000_000:.2f}B"
    if num >= 1_000_000:
        return f"${num / 1_000_000:.2f}M"
    return f"${num:,.2f}"


def _safe_get(info: dict, key: str, default: Any = None) -> Any:
    """Safely get a value from a dictionary."""
    value = info.get(key, default)
    return value if value is not None else default


@tool
def get_stock_quote(symbol: str) -> dict[str, Any]:
    """Get the current stock quote and trading information.

    Args:
        symbol: The stock ticker symbol (e.g., 'AAPL', 'MSFT', 'GOOGL')

    Returns:
        Dictionary containing current price, volume, and trading information
    """
    try:
        ticker = yf.Ticker(symbol.upper())
        info = ticker.info

        if not info or "symbol" not in info:
            return {"error": f"Stock symbol '{symbol}' not found"}

        current_price = _safe_get(info, "currentPrice") or _safe_get(info, "regularMarketPrice")
        previous_close = _safe_get(info, "previousClose") or _safe_get(info, "regularMarketPreviousClose")

        change = None
        change_percent = None
        if current_price and previous_close:
            change = current_price - previous_close
            change_percent = (change / previous_close) * 100

        return {
            "symbol": symbol.upper(),
            "name": _safe_get(info, "shortName") or _safe_get(info, "longName", symbol),
            "current_price": current_price,
            "previous_close": previous_close,
            "change": round(change, 2) if change else None,
            "change_percent": round(change_percent, 2) if change_percent else None,
            "day_high": _safe_get(info, "dayHigh") or _safe_get(info, "regularMarketDayHigh"),
            "day_low": _safe_get(info, "dayLow") or _safe_get(info, "regularMarketDayLow"),
            "volume": _safe_get(info, "volume") or _safe_get(info, "regularMarketVolume"),
            "avg_volume": _safe_get(info, "averageVolume"),
            "market_cap": _safe_get(info, "marketCap"),
            "market_cap_formatted": _format_large_number(_safe_get(info, "marketCap")),
            "fifty_two_week_high": _safe_get(info, "fiftyTwoWeekHigh"),
            "fifty_two_week_low": _safe_get(info, "fiftyTwoWeekLow"),
            "currency": _safe_get(info, "currency", "USD"),
        }
    except Exception as e:
        logger.error(f"Error fetching quote for {symbol}: {e}")
        return {"error": f"Failed to fetch quote for {symbol}: {str(e)}"}


@tool
def get_stock_metrics(symbol: str) -> dict[str, Any]:
    """Get fundamental metrics and financial ratios for a stock.

    Args:
        symbol: The stock ticker symbol (e.g., 'AAPL', 'MSFT', 'GOOGL')

    Returns:
        Dictionary containing P/E ratio, EPS, dividends, margins, and other metrics
    """
    try:
        ticker = yf.Ticker(symbol.upper())
        info = ticker.info

        if not info or "symbol" not in info:
            return {"error": f"Stock symbol '{symbol}' not found"}

        return {
            "symbol": symbol.upper(),
            "name": _safe_get(info, "shortName") or _safe_get(info, "longName", symbol),
            "sector": _safe_get(info, "sector"),
            "industry": _safe_get(info, "industry"),
            # Valuation Metrics
            "pe_ratio": _safe_get(info, "trailingPE"),
            "forward_pe": _safe_get(info, "forwardPE"),
            "peg_ratio": _safe_get(info, "pegRatio"),
            "price_to_book": _safe_get(info, "priceToBook"),
            "price_to_sales": _safe_get(info, "priceToSalesTrailing12Months"),
            "enterprise_value": _safe_get(info, "enterpriseValue"),
            "enterprise_value_formatted": _format_large_number(_safe_get(info, "enterpriseValue")),
            # Profitability
            "eps": _safe_get(info, "trailingEps"),
            "forward_eps": _safe_get(info, "forwardEps"),
            "profit_margin": _safe_get(info, "profitMargins"),
            "operating_margin": _safe_get(info, "operatingMargins"),
            "gross_margin": _safe_get(info, "grossMargins"),
            "return_on_equity": _safe_get(info, "returnOnEquity"),
            "return_on_assets": _safe_get(info, "returnOnAssets"),
            # Dividends
            "dividend_yield": _safe_get(info, "dividendYield"),
            "dividend_rate": _safe_get(info, "dividendRate"),
            "payout_ratio": _safe_get(info, "payoutRatio"),
            "ex_dividend_date": _safe_get(info, "exDividendDate"),
            # Growth
            "revenue_growth": _safe_get(info, "revenueGrowth"),
            "earnings_growth": _safe_get(info, "earningsGrowth"),
            "earnings_quarterly_growth": _safe_get(info, "earningsQuarterlyGrowth"),
            # Financial Health
            "total_debt": _safe_get(info, "totalDebt"),
            "total_cash": _safe_get(info, "totalCash"),
            "debt_to_equity": _safe_get(info, "debtToEquity"),
            "current_ratio": _safe_get(info, "currentRatio"),
            "quick_ratio": _safe_get(info, "quickRatio"),
            "free_cash_flow": _safe_get(info, "freeCashflow"),
            "free_cash_flow_formatted": _format_large_number(_safe_get(info, "freeCashflow")),
            # Other
            "beta": _safe_get(info, "beta"),
            "shares_outstanding": _safe_get(info, "sharesOutstanding"),
        }
    except Exception as e:
        logger.error(f"Error fetching metrics for {symbol}: {e}")
        return {"error": f"Failed to fetch metrics for {symbol}: {str(e)}"}


@tool
def compare_stocks(symbols: list[str]) -> dict[str, Any]:
    """Compare multiple stocks side by side with key metrics.

    Args:
        symbols: List of stock ticker symbols to compare (e.g., ['AAPL', 'MSFT', 'GOOGL'])

    Returns:
        Dictionary containing comparison data for all stocks
    """
    if not symbols:
        return {"error": "No symbols provided"}

    if len(symbols) > 10:
        return {"error": "Maximum 10 stocks can be compared at once"}

    comparisons = []
    errors = []

    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol.upper())
            info = ticker.info

            if not info or "symbol" not in info:
                errors.append(f"Symbol '{symbol}' not found")
                continue

            current_price = _safe_get(info, "currentPrice") or _safe_get(info, "regularMarketPrice")
            previous_close = _safe_get(info, "previousClose")
            change_percent = None
            if current_price and previous_close:
                change_percent = ((current_price - previous_close) / previous_close) * 100

            comparisons.append({
                "symbol": symbol.upper(),
                "name": _safe_get(info, "shortName") or _safe_get(info, "longName", symbol),
                "sector": _safe_get(info, "sector"),
                "industry": _safe_get(info, "industry"),
                "current_price": current_price,
                "change_percent": round(change_percent, 2) if change_percent else None,
                "market_cap": _safe_get(info, "marketCap"),
                "market_cap_formatted": _format_large_number(_safe_get(info, "marketCap")),
                "pe_ratio": _safe_get(info, "trailingPE"),
                "forward_pe": _safe_get(info, "forwardPE"),
                "peg_ratio": _safe_get(info, "pegRatio"),
                "eps": _safe_get(info, "trailingEps"),
                "dividend_yield": _safe_get(info, "dividendYield"),
                "profit_margin": _safe_get(info, "profitMargins"),
                "revenue_growth": _safe_get(info, "revenueGrowth"),
                "beta": _safe_get(info, "beta"),
                "fifty_two_week_high": _safe_get(info, "fiftyTwoWeekHigh"),
                "fifty_two_week_low": _safe_get(info, "fiftyTwoWeekLow"),
            })
        except Exception as e:
            logger.error(f"Error comparing {symbol}: {e}")
            errors.append(f"Failed to fetch data for {symbol}: {str(e)}")

    result = {
        "count": len(comparisons),
        "stocks": comparisons,
    }

    if errors:
        result["errors"] = errors

    return result


@tool
def get_stock_history(symbol: str, period: str = "1mo") -> dict[str, Any]:
    """Get historical price data for a stock.

    Args:
        symbol: The stock ticker symbol (e.g., 'AAPL', 'MSFT', 'GOOGL')
        period: Time period for historical data. Valid options:
                '1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'

    Returns:
        Dictionary containing historical price data with OHLCV information
    """
    valid_periods = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]

    if period not in valid_periods:
        return {
            "error": f"Invalid period: {period}",
            "valid_periods": valid_periods,
        }

    try:
        ticker = yf.Ticker(symbol.upper())
        history = ticker.history(period=period)

        if history.empty:
            return {"error": f"No historical data found for {symbol}"}

        # Calculate summary statistics
        prices = history["Close"].tolist()
        start_price = prices[0] if prices else None
        end_price = prices[-1] if prices else None
        total_return = None
        if start_price and end_price:
            total_return = ((end_price - start_price) / start_price) * 100

        # Get recent data points (last 10 for readability)
        recent_data = []
        for idx in range(min(10, len(history))):
            row = history.iloc[-(idx + 1)]
            recent_data.append({
                "date": str(history.index[-(idx + 1)].date()),
                "open": round(row["Open"], 2),
                "high": round(row["High"], 2),
                "low": round(row["Low"], 2),
                "close": round(row["Close"], 2),
                "volume": int(row["Volume"]),
            })
        recent_data.reverse()

        return {
            "symbol": symbol.upper(),
            "period": period,
            "data_points": len(history),
            "start_date": str(history.index[0].date()),
            "end_date": str(history.index[-1].date()),
            "start_price": round(start_price, 2) if start_price else None,
            "end_price": round(end_price, 2) if end_price else None,
            "total_return_percent": round(total_return, 2) if total_return else None,
            "high": round(history["High"].max(), 2),
            "low": round(history["Low"].min(), 2),
            "average_volume": int(history["Volume"].mean()),
            "recent_data": recent_data,
        }
    except Exception as e:
        logger.error(f"Error fetching history for {symbol}: {e}")
        return {"error": f"Failed to fetch history for {symbol}: {str(e)}"}
