from autogen_core.tools import FunctionTool


def get_ticker_info(ticker: str) -> str:
    """
    A tool to get stock information based on the provided ticker symbol.
    """
    # In a real implementation, you would fetch data from a financial API.
    # Here, we return a placeholder response.
    stock_data = {
        "PFC": "power finance corp is trading at $150.00 with a market cap of $50B.",
        "WAREE": "waree is trading at $75.00 with a market cap of $10B.",
        "NESTLE": "Nestle is trading at $200.00 with a market cap of $300B.",
    }
    return stock_data.get(ticker.upper(), f"No data found for ticker: {ticker}")


# Create the FunctionTool instance
ticker_tool = FunctionTool(
    get_ticker_info, description="Get stock information for a given ticker symbol"
)
