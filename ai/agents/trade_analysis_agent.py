from autogen_agentchat.agents import AssistantAgent
from ai.models import gtp_model_client
from ai.tools.ticker_tool import ticker_tool


def get_trade_analyst_agent(strategy_name: str) -> AssistantAgent:
    agent = AssistantAgent(
        name="TradeAnalysisAgent",
        model_client=gtp_model_client.get_openai_client(strategy_name),
        system_message="""
        You are a trade analysis expert. Provide insights and recommendations based on indian stock market data to know more about stock market tickers use ticker_tool 
        """,
        tools=[ticker_tool],
    )
    return agent
