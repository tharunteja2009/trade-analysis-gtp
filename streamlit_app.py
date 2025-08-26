import streamlit as st
import asyncio
from ai.agents.trade_analysis_agent import get_trade_analyst_agent
from autogen_agentchat.messages import (
    TextMessage,
    ToolCallSummaryMessage,
    ToolCallExecutionEvent,
)
from ai.teams.trade_recommendation_team import trade_recommendation_team
import json
import time
import ast
import re
from utils.number_formatter import format_large_number, format_data_for_console

# Configure Streamlit page
st.set_page_config(
    page_title="📈 Stock Trade Analysis",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom CSS for better styling
st.markdown(
    """
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.8rem;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1.5rem;
        border-bottom: 3px solid #3498db;
        padding-bottom: 0.5rem;
    }
    .data-summary {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 1rem;
        margin: 1.5rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .data-card {
        background-color: #ffffff;
        color: #333;
        padding: 1.2rem;
        border-radius: 0.8rem;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border-left: 4px solid #3498db;
    }
    .analysis-section {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 1rem;
        margin: 1.5rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .info-highlight {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2196f3;
        margin: 0.5rem 0;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
        margin: 0.5rem 0;
        border: 1px solid #dee2e6;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Title and description
st.markdown(
    '<h1 class="main-header">📈 AI-Powered Stock Trade Analysis</h1>',
    unsafe_allow_html=True,
)
st.markdown(
    "### Get comprehensive stock analysis with AI agents specializing in Indian stock market"
)

# Main input section
col1, col2 = st.columns([3, 1])

with col1:
    stock_name = st.text_input(
        "🏢 Enter Stock Name or Symbol",
        placeholder="e.g., TCS, HDFC Bank, CDSL, INFY",
        help="Enter Indian stock name or symbol (NSE/BSE)",
    )

with col2:
    st.write("")  # Add some spacing
    analyze_button = st.button(
        "🔍 Analyze Stock", type="primary", use_container_width=True
    )


# Function to run the analysis
async def run_analysis(stock_symbol):
    """Run the stock analysis using the agent team"""
    task = TextMessage(content=f"stock name : {stock_symbol}", source="user")
    team = trade_recommendation_team()
    result = await team.run(task=task)

    # Extract data from messages
    trade_final_analysis = None
    trade_data_collection = None

    for i, message in enumerate(result.messages):
        # Get the final analysis from TradeAnalysisAgent
        if isinstance(message, TextMessage) and message.source == "TradeAnalysisAgent":
            trade_final_analysis = message.content
        # Get the tool execution result (stock data)
        elif (
            isinstance(message, ToolCallExecutionEvent)
            and message.source == "TradedataCollectionAgent"
        ):
            if message.content and len(message.content) > 0:
                trade_data_collection = message.content[0].content
        elif (
            isinstance(message, ToolCallSummaryMessage)
            and message.source == "TradedataCollectionAgent"
        ):
            trade_data_collection = message.content

    return trade_final_analysis, trade_data_collection


# Function to safely parse data from string
def safe_parse_data(data):
    """Safely parse data string to dictionary, handling various formats"""
    if not data:
        return None

    if not isinstance(data, str):
        return data

    # Clean the data string first
    data_str = str(data).strip()

    # Handle pprint format (starts and ends with parentheses)
    if data_str.startswith("(") and data_str.endswith(")"):
        data_str = data_str[1:-1].strip()

    # Handle single or double quotes around the entire string
    if (data_str.startswith("'") and data_str.endswith("'")) or (
        data_str.startswith('"') and data_str.endswith('"')
    ):
        data_str = data_str[1:-1]

    # Try multiple parsing strategies
    parsing_strategies = [
        # Strategy 1: Try JSON parsing first
        lambda d: json.loads(d),
        # Strategy 2: Try direct eval if it looks like a dict
        lambda d: (
            eval(d) if d.strip().startswith("{") and d.strip().endswith("}") else None
        ),
        # Strategy 3: Try ast.literal_eval directly
        lambda d: ast.literal_eval(d),
        # Strategy 4: Fix leading zeros and try ast.literal_eval
        lambda d: ast.literal_eval(re.sub(r":\s*0+(\d)", r": \1", d)),
        # Strategy 5: More aggressive leading zero fix
        lambda d: ast.literal_eval(re.sub(r"(\W)0+(\d)", r"\1\2", d)),
        # Strategy 6: Replace problematic numbers with strings and parse
        lambda d: ast.literal_eval(re.sub(r":\s*0+(\d+)", r': "\1"', d)),
        # Strategy 7: Handle multiline strings by replacing newlines
        lambda d: ast.literal_eval(re.sub(r"\n\s*", " ", d)),
        # Strategy 8: Try to extract just the dictionary part if it's embedded
        lambda d: (
            ast.literal_eval(re.search(r"\{.*\}", d, re.DOTALL).group())
            if re.search(r"\{.*\}", d, re.DOTALL)
            else None
        ),
    ]

    for i, strategy in enumerate(parsing_strategies):
        try:
            result = strategy(data_str)
            if result is not None and isinstance(result, dict):
                return result
        except Exception as e:
            continue

    # If all parsing fails, return None
    return None


# Function to display stock data in console format
def display_console_format_data(data):
    """Display stock data in the same format as console output"""
    if not data:
        st.warning("No data available")
        return

    # Create the console-style header
    st.markdown(
        """
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 1rem;
        margin: 1.5rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        text-align: center;
    ">
        <h2 style="margin: 0; font-family: 'Courier New', monospace;">
            ============================================================<br>
            📈 DATA CONSIDERED FOR STOCK ANALYSIS<br>
            ============================================================
        </h2>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Display the raw data in a simple text scroller format

    # Convert data to string format for display with formatted numbers
    if data:
        try:
            # Try to format the data first
            formatted_data = format_data_for_console(data)
            data_str = str(formatted_data)
        except:
            # If formatting fails, use original data
            data_str = str(data)
    else:
        data_str = "No data available"

    # Create a simple text area with the raw data for easy reading
    st.text_area(
        "Raw Stock Data (Scrollable):",
        value=data_str,
        height=400,
        help="This is the exact data that Agent 1 collected and passed to Agent 2 for analysis",
    )

    # Also try to parse and display in a cleaner format if possible
    try:
        data_dict = safe_parse_data(data)
        if data_dict and isinstance(data_dict, dict):
            st.markdown("### � Parsed Data Summary")

            # Create expandable sections for different data types
            with st.expander("🏷️ Basic Stock Information", expanded=True):
                basic_info = {
                    "Ticker": data_dict.get("Ticker", "N/A"),
                    "Current Price": data_dict.get("Current Price", "N/A"),
                    "Open": data_dict.get("Open", "N/A"),
                    "Day High": data_dict.get("Day High", "N/A"),
                    "Day Low": data_dict.get("Day Low", "N/A"),
                    "Volume": data_dict.get("Volume", "N/A"),
                    "52-Week High": data_dict.get("52-Week High", "N/A"),
                    "52-Week Low": data_dict.get("52-Week Low", "N/A"),
                }

                # Display in columns for better layout
                col1, col2 = st.columns(2)
                for i, (key, value) in enumerate(basic_info.items()):
                    if i % 2 == 0:
                        col1.metric(label=key, value=str(value))
                    else:
                        col2.metric(label=key, value=str(value))

            if "Fundamentals" in data_dict and data_dict["Fundamentals"]:
                with st.expander("📊 Financial Fundamentals"):
                    fundamentals = data_dict["Fundamentals"]
                    st.json(fundamentals)

            if "Company Info" in data_dict and data_dict["Company Info"]:
                with st.expander("🏢 Company Information"):
                    company_info = data_dict["Company Info"]
                    st.json(company_info)

    except Exception as e:
        st.info(
            f"Could not parse structured data, showing raw format above. ({str(e)[:100]})"
        )


# Main analysis logic
if analyze_button and stock_name:
    if not stock_name.strip():
        st.error("Please enter a valid stock name or symbol")
    else:
        # Show loading message
        with st.spinner(f"🔍 Analyzing {stock_name.upper()}..."):
            try:
                # Run the analysis
                final_analysis, stock_data = asyncio.run(
                    run_analysis(stock_name.strip())
                )

                # Display results
                if stock_data or final_analysis:
                    if stock_data:
                        display_console_format_data(stock_data)

                    if final_analysis:
                        st.markdown(
                            """
                            <div class="analysis-section">
                                <h2 style="margin-top: 0;">🧠 AI Analysis & Investment Recommendation</h2>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                        st.markdown(final_analysis)
                else:
                    st.error("No analysis results received. Please try again.")

            except Exception as e:
                st.error(f"An error occurred during analysis: {str(e)}")

elif analyze_button:
    st.warning("Please enter a stock name or symbol to analyze")

# Footer
st.markdown("---")
st.markdown(
    """
<div style='text-align: center; color: #666;'>
    <p>AI-Powered Stock Analysis • Built with Streamlit & AutoGen Agents</p>
    <p><small>⚠️ This is for educational purposes only. Not financial advice.</small></p>
</div>
""",
    unsafe_allow_html=True,
)

# Sample stocks for easy testing
with st.sidebar:
    st.markdown("### 📋 Sample Stocks to Try")
    sample_stocks = ["TCS", "HDFC Bank", "CDSL", "INFY", "RELIANCE", "ITC"]

    for stock in sample_stocks:
        if st.button(f"📊 {stock}", key=f"sample_{stock}", use_container_width=True):
            st.session_state.stock_input = stock
            st.rerun()

# Handle sample stock selection
if "stock_input" in st.session_state:
    stock_name = st.session_state.stock_input
    del st.session_state.stock_input
