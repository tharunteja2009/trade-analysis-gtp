from ai.agents.trade_analysis_agent import get_trade_analyst_agent
from autogen_agentchat.messages import (
    TextMessage,
    ToolCallSummaryMessage,
    ToolCallExecutionEvent,
)
from ai.teams.trade_recommendation_team import trade_recommendation_team
import asyncio
from pprint import pprint
from utils.number_formatter import format_data_for_console
from utils.cost_tracker import start_tracking, get_session_summary, format_cost_summary
from utils.autogen_tracker import (
    track_autogen_result,
    get_team_summary,
    format_team_summary,
    parse_stock_data_for_tracking,
)


async def main():
    # Start cost tracking session
    session_id = start_tracking("console_stock_analysis")
    print("🔢 Started token usage tracking for this analysis session...")

    model_strategy = "economic-task"  # Using depth-analysis for better results
    stock_name = input("Enter stock name or symbol for analysis : ")
    task = TextMessage(content=f"stock name : {stock_name}", source="user")
    team = trade_recommendation_team()

    print(f"📊 Analyzing {stock_name}... (tracking token usage)")
    result = await team.run(task=task)

    # Track AutoGen team conversation
    track_autogen_result(result)

    # pprint(f"{result}")

    # Extract and print only the final analysis from agents
    trade_final_analysis = None
    trade_data_collection = None

    for message in result.messages:
        # Get the final analysis from TradeAnalysisAgent
        if isinstance(message, TextMessage) and message.source == "TradeAnalysisAgent":
            trade_final_analysis = message.content
        # Get the tool execution result (stock data) - using correct agent name
        elif (
            isinstance(message, ToolCallExecutionEvent)
            and message.source == "TradedataCollectionAgent"
        ):
            # Extract the actual function result content
            if message.content and len(message.content) > 0:
                trade_data_collection = message.content[0].content
        elif (
            isinstance(message, ToolCallSummaryMessage)
            and message.source == "TradedataCollectionAgent"
        ):
            trade_data_collection = message.content

    print("\n" + "=" * 60)
    print("📈 DATA CONSIDERED FOR STOCK ANALYSIS")
    print("=" * 60)

    # Format the data before printing and track data parsing
    formatted_data = format_data_for_console(trade_data_collection)

    # Parse stock data for detailed token tracking
    if trade_data_collection:
        data_sections = parse_stock_data_for_tracking(trade_data_collection)
        print(f"📊 Data sections processed: {list(data_sections.keys())}")

    pprint(formatted_data)

    print("=" * 60)
    print("\n" + "=" * 60)
    print("📈 STOCK ANALYSIS REPORT")
    print("=" * 60)
    pprint(trade_final_analysis)
    print("=" * 60)

    # Display comprehensive cost and usage summary
    print("\n" + "💰" * 60)
    print("TOKEN USAGE & COST SUMMARY")
    print("💰" * 60)

    # Session summary (exact usage if available)
    session_summary = get_session_summary()
    if session_summary.strip():
        print(session_summary)
    else:
        print(
            "📝 Exact token usage data not available (AutoGen doesn't expose token counts)"
        )

    # Team conversation summary (estimated)
    team_summary = get_team_summary()
    if team_summary and team_summary.get("total_estimated_tokens", 0) > 0:
        print("\n" + format_team_summary(team_summary))

    print("\n💡 Note: Token estimates are based on text length analysis.")
    print("   Actual costs may vary based on the specific model's tokenization.")
    print("💰" * 60)


if __name__ == "__main__":
    asyncio.run(main())
