"""Analysis tools for stock recommendations and insights."""

import logging
from datetime import datetime
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


@tool
def get_analyst_recommendations(symbol: str) -> dict[str, Any]:
    """Get analyst ratings, recommendations, and price targets for a stock.

    Args:
        symbol: The stock ticker symbol (e.g., 'AAPL', 'MSFT', 'GOOGL')

    Returns:
        Dictionary containing analyst recommendations, ratings distribution,
        and price targets
    """
    try:
        ticker = yf.Ticker(symbol.upper())
        info = ticker.info

        if not info or "symbol" not in info:
            return {"error": f"Stock symbol '{symbol}' not found"}

        # Get recommendation trend
        recommendations = None
        try:
            rec_df = ticker.recommendations
            if rec_df is not None and not rec_df.empty:
                recent_recs = rec_df.tail(10)
                recommendations = []
                for idx, row in recent_recs.iterrows():
                    rec = {
                        "date": str(idx.date()) if hasattr(idx, "date") else str(idx),
                        "firm": row.get("Firm", "Unknown"),
                        "to_grade": row.get("To Grade", row.get("toGrade", "N/A")),
                        "from_grade": row.get("From Grade", row.get("fromGrade", "N/A")),
                        "action": row.get("Action", row.get("action", "N/A")),
                    }
                    recommendations.append(rec)
        except Exception as e:
            logger.warning(f"Could not fetch recommendations for {symbol}: {e}")

        current_price = info.get("currentPrice") or info.get("regularMarketPrice")

        result = {
            "symbol": symbol.upper(),
            "name": info.get("shortName") or info.get("longName", symbol),
            "current_price": current_price,
            # Analyst ratings
            "recommendation": info.get("recommendationKey"),
            "recommendation_mean": info.get("recommendationMean"),
            "number_of_analysts": info.get("numberOfAnalystOpinions"),
            # Price targets
            "target_high": info.get("targetHighPrice"),
            "target_low": info.get("targetLowPrice"),
            "target_mean": info.get("targetMeanPrice"),
            "target_median": info.get("targetMedianPrice"),
        }

        # Calculate upside/downside potential
        if current_price and result["target_mean"]:
            upside = ((result["target_mean"] - current_price) / current_price) * 100
            result["upside_potential_percent"] = round(upside, 2)

        # Add recent recommendations if available
        if recommendations:
            result["recent_recommendations"] = recommendations

        return result
    except Exception as e:
        logger.error(f"Error fetching analyst data for {symbol}: {e}")
        return {"error": f"Failed to fetch analyst data for {symbol}: {str(e)}"}


@tool
def get_stock_news(symbol: str, limit: int = 5) -> dict[str, Any]:
    """Get recent news articles and headlines for a stock.

    Args:
        symbol: The stock ticker symbol (e.g., 'AAPL', 'MSFT', 'GOOGL')
        limit: Maximum number of news articles to return (default: 5, max: 10)

    Returns:
        Dictionary containing recent news articles with titles, links, and summaries
    """
    limit = min(limit, 10)

    try:
        ticker = yf.Ticker(symbol.upper())
        news = ticker.news

        if not news:
            return {
                "symbol": symbol.upper(),
                "count": 0,
                "news": [],
                "message": "No recent news available",
            }

        articles = []
        for item in news[:limit]:
            article = {
                "title": item.get("title", "No title"),
                "publisher": item.get("publisher", "Unknown"),
                "link": item.get("link", ""),
                "type": item.get("type", "article"),
            }

            # Format publish time if available
            publish_time = item.get("providerPublishTime")
            if publish_time:
                try:
                    dt = datetime.fromtimestamp(publish_time)
                    article["published"] = dt.strftime("%Y-%m-%d %H:%M")
                except Exception:
                    pass

            # Include thumbnail if available
            thumbnail = item.get("thumbnail")
            if thumbnail and isinstance(thumbnail, dict):
                resolutions = thumbnail.get("resolutions", [])
                if resolutions:
                    article["thumbnail_url"] = resolutions[0].get("url")

            articles.append(article)

        return {
            "symbol": symbol.upper(),
            "count": len(articles),
            "news": articles,
        }
    except Exception as e:
        logger.error(f"Error fetching news for {symbol}: {e}")
        return {"error": f"Failed to fetch news for {symbol}: {str(e)}"}


@tool
def analyze_stock_value(symbol: str) -> dict[str, Any]:
    """Analyze a stock's valuation and provide buy/hold/sell signals.

    This tool evaluates multiple factors including P/E ratio, PEG ratio,
    price vs analyst targets, and other metrics to provide an overall
    assessment of the stock's value.

    Args:
        symbol: The stock ticker symbol (e.g., 'AAPL', 'MSFT', 'GOOGL')

    Returns:
        Dictionary containing valuation analysis with signals and insights
    """
    try:
        ticker = yf.Ticker(symbol.upper())
        info = ticker.info

        if not info or "symbol" not in info:
            return {"error": f"Stock symbol '{symbol}' not found"}

        current_price = info.get("currentPrice") or info.get("regularMarketPrice")
        signals = []
        positive_factors = []
        negative_factors = []
        neutral_factors = []

        # P/E Ratio Analysis
        pe_ratio = info.get("trailingPE")
        forward_pe = info.get("forwardPE")
        if pe_ratio:
            if pe_ratio < 15:
                positive_factors.append(f"Low P/E ratio ({pe_ratio:.1f}) suggests undervaluation")
            elif pe_ratio > 30:
                negative_factors.append(f"High P/E ratio ({pe_ratio:.1f}) suggests overvaluation")
            else:
                neutral_factors.append(f"P/E ratio ({pe_ratio:.1f}) is within normal range")

        # Forward P/E vs Trailing P/E
        if pe_ratio and forward_pe:
            if forward_pe < pe_ratio * 0.85:
                positive_factors.append("Earnings expected to grow (forward P/E lower than trailing)")

        # PEG Ratio Analysis
        peg_ratio = info.get("pegRatio")
        if peg_ratio:
            if peg_ratio < 1:
                positive_factors.append(f"PEG ratio ({peg_ratio:.2f}) under 1 suggests good value for growth")
            elif peg_ratio > 2:
                negative_factors.append(f"High PEG ratio ({peg_ratio:.2f}) suggests overvalued for growth rate")

        # Price vs 52-week range
        week_high = info.get("fiftyTwoWeekHigh")
        week_low = info.get("fiftyTwoWeekLow")
        if current_price and week_high and week_low:
            position = (current_price - week_low) / (week_high - week_low) * 100
            if position < 30:
                positive_factors.append(f"Trading near 52-week low (bottom {position:.0f}% of range)")
            elif position > 80:
                negative_factors.append(f"Trading near 52-week high (top {100-position:.0f}% of range)")

        # Analyst Target Analysis
        target_mean = info.get("targetMeanPrice")
        if current_price and target_mean:
            upside = ((target_mean - current_price) / current_price) * 100
            if upside > 20:
                positive_factors.append(f"Significant upside to analyst target ({upside:.1f}%)")
            elif upside < -10:
                negative_factors.append(f"Trading above analyst target ({upside:.1f}% downside)")

        # Dividend Analysis
        dividend_yield = info.get("dividendYield")
        if dividend_yield:
            if dividend_yield > 0.03:
                positive_factors.append(f"Good dividend yield ({dividend_yield*100:.2f}%)")

        # Profit Margin
        profit_margin = info.get("profitMargins")
        if profit_margin:
            if profit_margin > 0.20:
                positive_factors.append(f"Strong profit margins ({profit_margin*100:.1f}%)")
            elif profit_margin < 0.05:
                negative_factors.append(f"Weak profit margins ({profit_margin*100:.1f}%)")

        # Revenue Growth
        revenue_growth = info.get("revenueGrowth")
        if revenue_growth:
            if revenue_growth > 0.15:
                positive_factors.append(f"Strong revenue growth ({revenue_growth*100:.1f}%)")
            elif revenue_growth < 0:
                negative_factors.append(f"Negative revenue growth ({revenue_growth*100:.1f}%)")

        # Debt Analysis
        debt_to_equity = info.get("debtToEquity")
        if debt_to_equity:
            if debt_to_equity > 200:
                negative_factors.append(f"High debt-to-equity ratio ({debt_to_equity:.0f}%)")
            elif debt_to_equity < 50:
                positive_factors.append(f"Low debt-to-equity ratio ({debt_to_equity:.0f}%)")

        # Calculate overall signal
        positive_count = len(positive_factors)
        negative_count = len(negative_factors)

        if positive_count >= negative_count + 2:
            overall_signal = "BULLISH"
            signal_description = "Multiple positive indicators suggest good value"
        elif negative_count >= positive_count + 2:
            overall_signal = "BEARISH"
            signal_description = "Multiple negative indicators suggest caution"
        else:
            overall_signal = "NEUTRAL"
            signal_description = "Mixed signals - further research recommended"

        return {
            "symbol": symbol.upper(),
            "name": info.get("shortName") or info.get("longName", symbol),
            "current_price": current_price,
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "overall_signal": overall_signal,
            "signal_description": signal_description,
            "positive_factors": positive_factors,
            "negative_factors": negative_factors,
            "neutral_factors": neutral_factors,
            "key_metrics": {
                "pe_ratio": pe_ratio,
                "forward_pe": forward_pe,
                "peg_ratio": peg_ratio,
                "price_to_book": info.get("priceToBook"),
                "dividend_yield": dividend_yield,
                "profit_margin": profit_margin,
                "revenue_growth": revenue_growth,
                "debt_to_equity": debt_to_equity,
                "analyst_target": target_mean,
                "analyst_recommendation": info.get("recommendationKey"),
            },
            "disclaimer": "This analysis is for informational purposes only and should not be considered financial advice.",
        }
    except Exception as e:
        logger.error(f"Error analyzing {symbol}: {e}")
        return {"error": f"Failed to analyze {symbol}: {str(e)}"}
