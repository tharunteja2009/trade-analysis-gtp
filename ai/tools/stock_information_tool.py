import yfinance as yf
from autogen_core.tools import FunctionTool
from typing import Dict, Any


def get_full_stock_info(ticker_symbol: str) -> Dict[str, Any]:
    # Try to fetch ticker info, and if it fails for Indian stocks, try with .NS suffix
    original_ticker = ticker_symbol.upper()
    ticker = yf.Ticker(original_ticker)

    # Check if this is likely an Indian stock (no dots in ticker and data not available)
    try:
        info = ticker.info
        # If we get minimal info, this might be an invalid ticker
        if (
            not info.get("currentPrice")
            and not info.get("regularMarketPrice")
            and "." not in original_ticker
        ):
            # Try with .NS suffix for NSE stocks
            nse_ticker = original_ticker + ".NS"
            ticker = yf.Ticker(nse_ticker)
            ticker_symbol = nse_ticker
        else:
            ticker_symbol = original_ticker
    except:
        # If there's an error, try with .NS suffix
        if "." not in original_ticker:
            nse_ticker = original_ticker + ".NS"
            ticker = yf.Ticker(nse_ticker)
            ticker_symbol = nse_ticker
        else:
            ticker_symbol = original_ticker

    # Current market info
    info = ticker.info
    current_price = info.get("currentPrice")
    open_price = info.get("open")
    day_high = info.get("dayHigh")
    day_low = info.get("dayLow")
    volume = info.get("volume")

    # 52-week high and low
    fifty_two_week_high = info.get("fiftyTwoWeekHigh")
    fifty_two_week_low = info.get("fiftyTwoWeekLow")

    # All-time high and low from history
    hist = ticker.history(period="max")
    all_time_high = hist["Close"].max()
    all_time_low = hist["Close"].min()

    # Fundamental statistics
    fundamentals = {
        "Market Cap": info.get("marketCap"),
        "Trailing P/E": info.get("trailingPE"),
        "Forward P/E": info.get("forwardPE"),
        "PEG Ratio": info.get("pegRatio"),
        "Price to Book": info.get("priceToBook"),
        "Dividend Yield": info.get("dividendYield"),
        "Beta": info.get("beta"),
        "52 Week Change": info.get("52WeekChange"),
        "Profit Margins": info.get("profitMargins"),
    }

    # Company info
    company_info = {
        "Name": info.get("longName"),
        "Sector": info.get("sector"),
        "Industry": info.get("industry"),
        "Full Time Employees": info.get("fullTimeEmployees"),
        "Website": info.get("website"),
        "Description": info.get("longBusinessSummary"),
    }

    # Financial statements
    financials = {
        "Income Statement": ticker.financials,
        "Balance Sheet": ticker.balance_sheet,
        "Cash Flow": ticker.cashflow,
    }

    # Major holders
    holders = {
        "Institutional Holders": ticker.institutional_holders,
        "Mutual Fund Holders": ticker.mutualfund_holders,
        "Major Holders": ticker.major_holders,
    }

    # Combine everything
    full_data = {
        "Ticker": ticker_symbol.upper(),
        "Current Price": current_price,
        "Open": open_price,
        "Day High": day_high,
        "Day Low": day_low,
        "Volume": volume,
        "52-Week High": fifty_two_week_high,
        "52-Week Low": fifty_two_week_low,
        "All-Time High": all_time_high,
        "All-Time Low": all_time_low,
        "Fundamentals": fundamentals,
        "Company Info": company_info,
        "Financials": financials,
        "Holders": holders,
    }
    return full_data


ticker_tool = FunctionTool(
    get_full_stock_info,
    description="This tool provide information of stock",
)
