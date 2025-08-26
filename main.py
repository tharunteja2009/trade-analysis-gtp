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


async def main():
    model_strategy = "economic-task"  # Using depth-analysis for better results
    stock_name = input("Enter stock name or symbol for analysis : ")
    task = TextMessage(content=f"stock name : {stock_name}", source="user")
    team = trade_recommendation_team()
    result = await team.run(task=task)

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

    # Format the data before printing
    formatted_data = format_data_for_console(trade_data_collection)
    pprint(formatted_data)

    print("=" * 60)
    print("\n" + "=" * 60)
    print("📈 STOCK ANALYSIS REPORT")
    print("=" * 60)
    pprint(trade_final_analysis)
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
