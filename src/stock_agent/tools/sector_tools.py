"""Sector and industry tools for stock discovery."""

import logging
from typing import Any

import yfinance as yf
from strands import tool

logger = logging.getLogger(__name__)

# Mapping of sectors to representative ETFs and top holdings
SECTOR_ETFS = {
    "technology": "XLK",
    "healthcare": "XLV",
    "financial": "XLF",
    "financials": "XLF",
    "consumer discretionary": "XLY",
    "consumer staples": "XLP",
    "energy": "XLE",
    "industrials": "XLI",
    "materials": "XLB",
    "utilities": "XLU",
    "real estate": "XLRE",
    "communication services": "XLC",
    "communications": "XLC",
}

# Top stocks by sector (fallback when ETF data unavailable)
SECTOR_STOCKS = {
    "technology": [
        "AAPL", "MSFT", "NVDA", "GOOGL", "META", "AVGO", "ORCL", "CSCO", "CRM", "AMD",
        "ADBE", "ACN", "IBM", "INTC", "QCOM", "TXN", "NOW", "INTU", "AMAT", "MU"
    ],
    "healthcare": [
        "UNH", "JNJ", "LLY", "PFE", "ABBV", "MRK", "TMO", "ABT", "DHR", "BMY",
        "AMGN", "MDT", "GILD", "CVS", "ELV", "CI", "ISRG", "VRTX", "SYK", "REGN"
    ],
    "financial": [
        "BRK-B", "JPM", "V", "MA", "BAC", "WFC", "GS", "MS", "SPGI", "BLK",
        "C", "AXP", "SCHW", "CB", "MMC", "PGR", "AON", "CME", "ICE", "USB"
    ],
    "financials": [
        "BRK-B", "JPM", "V", "MA", "BAC", "WFC", "GS", "MS", "SPGI", "BLK",
        "C", "AXP", "SCHW", "CB", "MMC", "PGR", "AON", "CME", "ICE", "USB"
    ],
    "consumer discretionary": [
        "AMZN", "TSLA", "HD", "MCD", "NKE", "LOW", "SBUX", "TJX", "BKNG", "MAR",
        "CMG", "ORLY", "AZO", "ROST", "DHI", "LEN", "GM", "F", "YUM", "DG"
    ],
    "consumer staples": [
        "PG", "KO", "PEP", "COST", "WMT", "PM", "MO", "MDLZ", "CL", "EL",
        "GIS", "KMB", "SYY", "HSY", "K", "KHC", "CAG", "CLX", "SJM", "MKC"
    ],
    "energy": [
        "XOM", "CVX", "COP", "SLB", "EOG", "MPC", "PSX", "VLO", "PXD", "OXY",
        "WMB", "KMI", "HAL", "DVN", "HES", "FANG", "BKR", "TRGP", "OKE", "MRO"
    ],
    "industrials": [
        "CAT", "UNP", "HON", "UPS", "BA", "RTX", "DE", "LMT", "GE", "MMM",
        "ADP", "ITW", "EMR", "FDX", "NSC", "CSX", "JCI", "PH", "ROK", "ETN"
    ],
    "materials": [
        "LIN", "APD", "SHW", "ECL", "FCX", "NEM", "NUE", "DOW", "DD", "PPG",
        "VMC", "MLM", "ALB", "IFF", "CE", "LYB", "CF", "MOS", "CTVA", "FMC"
    ],
    "utilities": [
        "NEE", "DUK", "SO", "D", "AEP", "SRE", "EXC", "XEL", "PEG", "ED",
        "WEC", "ES", "AWK", "DTE", "ETR", "FE", "PPL", "AEE", "CMS", "EVRG"
    ],
    "real estate": [
        "PLD", "AMT", "EQIX", "CCI", "PSA", "SPG", "O", "WELL", "DLR", "AVB",
        "EQR", "VTR", "ARE", "MAA", "UDR", "ESS", "REG", "BXP", "KIM", "HST"
    ],
    "communication services": [
        "GOOGL", "META", "NFLX", "DIS", "CMCSA", "T", "VZ", "TMUS", "CHTR", "EA",
        "ATVI", "TTWO", "WBD", "PARA", "FOX", "OMC", "IPG", "LYV", "MTCH", "ZG"
    ],
    "communications": [
        "GOOGL", "META", "NFLX", "DIS", "CMCSA", "T", "VZ", "TMUS", "CHTR", "EA",
        "ATVI", "TTWO", "WBD", "PARA", "FOX", "OMC", "IPG", "LYV", "MTCH", "ZG"
    ],
}

# Industries within sectors
SECTOR_INDUSTRIES = {
    "technology": [
        "Software - Application", "Software - Infrastructure", "Semiconductors",
        "Information Technology Services", "Consumer Electronics", "Electronic Components",
        "Computer Hardware", "Scientific & Technical Instruments", "Communication Equipment"
    ],
    "healthcare": [
        "Drug Manufacturers", "Biotechnology", "Medical Devices", "Healthcare Plans",
        "Medical Instruments & Supplies", "Diagnostics & Research", "Medical Care Facilities",
        "Pharmaceutical Retailers", "Health Information Services"
    ],
    "financial": [
        "Banks - Diversified", "Insurance - Life", "Asset Management", "Credit Services",
        "Insurance - Property & Casualty", "Capital Markets", "Banks - Regional",
        "Financial Data & Stock Exchanges", "Insurance Brokers"
    ],
    "financials": [
        "Banks - Diversified", "Insurance - Life", "Asset Management", "Credit Services",
        "Insurance - Property & Casualty", "Capital Markets", "Banks - Regional",
        "Financial Data & Stock Exchanges", "Insurance Brokers"
    ],
    "consumer discretionary": [
        "Internet Retail", "Auto Manufacturers", "Restaurants", "Home Improvement Retail",
        "Apparel Retail", "Specialty Retail", "Leisure", "Residential Construction",
        "Footwear & Accessories", "Travel Services"
    ],
    "consumer staples": [
        "Household & Personal Products", "Beverages - Soft Drinks", "Packaged Foods",
        "Discount Stores", "Tobacco", "Food Distribution", "Grocery Stores",
        "Beverages - Alcoholic", "Farm Products"
    ],
    "energy": [
        "Oil & Gas Integrated", "Oil & Gas E&P", "Oil & Gas Midstream",
        "Oil & Gas Refining & Marketing", "Oil & Gas Equipment & Services",
        "Oil & Gas Drilling", "Uranium"
    ],
    "industrials": [
        "Aerospace & Defense", "Railroads", "Farm & Heavy Construction Machinery",
        "Industrial Distribution", "Specialty Industrial Machinery", "Conglomerates",
        "Airlines", "Trucking", "Building Products", "Engineering & Construction"
    ],
    "materials": [
        "Specialty Chemicals", "Gold", "Copper", "Steel", "Building Materials",
        "Agricultural Inputs", "Paper & Paper Products", "Aluminum", "Chemicals"
    ],
    "utilities": [
        "Utilities - Regulated Electric", "Utilities - Diversified",
        "Utilities - Regulated Gas", "Utilities - Renewable", "Utilities - Water"
    ],
    "real estate": [
        "REIT - Industrial", "REIT - Retail", "REIT - Residential", "REIT - Office",
        "REIT - Healthcare Facilities", "REIT - Diversified", "REIT - Specialty",
        "Real Estate Services", "Real Estate Development"
    ],
    "communication services": [
        "Internet Content & Information", "Entertainment", "Telecom Services",
        "Electronic Gaming & Multimedia", "Advertising Agencies", "Broadcasting",
        "Publishing"
    ],
    "communications": [
        "Internet Content & Information", "Entertainment", "Telecom Services",
        "Electronic Gaming & Multimedia", "Advertising Agencies", "Broadcasting",
        "Publishing"
    ],
}


def _normalize_sector(sector: str) -> str:
    """Normalize sector name to match our mappings."""
    return sector.lower().strip()


def _get_stock_info(symbol: str) -> dict[str, Any]:
    """Get basic stock info from yfinance."""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        return {
            "symbol": symbol,
            "name": info.get("shortName", info.get("longName", symbol)),
            "sector": info.get("sector", "Unknown"),
            "industry": info.get("industry", "Unknown"),
            "market_cap": info.get("marketCap"),
            "current_price": info.get("currentPrice", info.get("regularMarketPrice")),
        }
    except Exception as e:
        logger.warning(f"Error fetching info for {symbol}: {e}")
        return {"symbol": symbol, "name": symbol, "error": str(e)}


@tool
def get_stocks_by_sector(sector: str, limit: int = 10) -> dict[str, Any]:
    """Get top stocks in a specific market sector.

    Args:
        sector: The market sector (e.g., 'technology', 'healthcare', 'financial', 'energy',
                'consumer discretionary', 'consumer staples', 'industrials', 'materials',
                'utilities', 'real estate', 'communication services')
        limit: Maximum number of stocks to return (default: 10, max: 20)

    Returns:
        Dictionary containing sector stocks with their basic information
    """
    normalized_sector = _normalize_sector(sector)
    limit = min(limit, 20)

    if normalized_sector not in SECTOR_STOCKS:
        available_sectors = list(set(SECTOR_STOCKS.keys()) - {"financials", "communications"})
        return {
            "error": f"Unknown sector: {sector}",
            "available_sectors": sorted(available_sectors),
        }

    stock_symbols = SECTOR_STOCKS[normalized_sector][:limit]
    stocks = []

    for symbol in stock_symbols:
        stock_info = _get_stock_info(symbol)
        if "error" not in stock_info:
            stocks.append(stock_info)

    return {
        "sector": sector,
        "count": len(stocks),
        "stocks": stocks,
    }


@tool
def get_stocks_by_industry(industry: str, limit: int = 10) -> dict[str, Any]:
    """Get stocks in a specific industry using yfinance screening.

    Args:
        industry: The industry name (e.g., 'Semiconductors', 'Biotechnology', 'Software - Application')
        limit: Maximum number of stocks to return (default: 10, max: 15)

    Returns:
        Dictionary containing industry stocks with their basic information
    """
    limit = min(limit, 15)
    industry_lower = industry.lower()

    # Find which sector this industry belongs to for getting candidate stocks
    candidate_stocks = []
    found_sector = None

    for sector, industries in SECTOR_INDUSTRIES.items():
        for ind in industries:
            if industry_lower in ind.lower() or ind.lower() in industry_lower:
                found_sector = sector
                break
        if found_sector:
            break

    # Get candidate stocks from the sector
    if found_sector and found_sector in SECTOR_STOCKS:
        candidate_stocks = SECTOR_STOCKS[found_sector]
    else:
        # Search across all sectors
        for sector_stocks in SECTOR_STOCKS.values():
            candidate_stocks.extend(sector_stocks)
        candidate_stocks = list(set(candidate_stocks))

    # Filter stocks by industry
    matching_stocks = []
    for symbol in candidate_stocks:
        if len(matching_stocks) >= limit:
            break
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            stock_industry = info.get("industry", "").lower()
            if industry_lower in stock_industry or stock_industry in industry_lower:
                matching_stocks.append({
                    "symbol": symbol,
                    "name": info.get("shortName", info.get("longName", symbol)),
                    "sector": info.get("sector", "Unknown"),
                    "industry": info.get("industry", "Unknown"),
                    "market_cap": info.get("marketCap"),
                    "current_price": info.get("currentPrice", info.get("regularMarketPrice")),
                })
        except Exception as e:
            logger.warning(f"Error checking industry for {symbol}: {e}")
            continue

    return {
        "industry": industry,
        "count": len(matching_stocks),
        "stocks": matching_stocks,
    }


@tool
def list_industries_in_sector(sector: str) -> dict[str, Any]:
    """List all industries within a specific market sector.

    Args:
        sector: The market sector (e.g., 'technology', 'healthcare', 'financial')

    Returns:
        Dictionary containing the list of industries in the sector
    """
    normalized_sector = _normalize_sector(sector)

    if normalized_sector not in SECTOR_INDUSTRIES:
        available_sectors = list(set(SECTOR_INDUSTRIES.keys()) - {"financials", "communications"})
        return {
            "error": f"Unknown sector: {sector}",
            "available_sectors": sorted(available_sectors),
        }

    industries = SECTOR_INDUSTRIES[normalized_sector]

    return {
        "sector": sector,
        "count": len(industries),
        "industries": industries,
    }
