from ai.models.gtp_model_client import get_openai_client
from ai.agents.trade_analysis_agent import get_trade_analyst_agent
from autogen_agentchat.messages import TextMessage
import asyncio


async def main():
    # Example usage of the get_openai_client function
    model_strategy = (
        "economic-task"  # This can be changed to "deapth-analysis" as needed
    )
    client = get_openai_client(model_strategy)
    print(f"Initialized model for strategy: {model_strategy}")
    agent = get_trade_analyst_agent(model_strategy)
    stock_name = input("Enter stock name or symbol for analysis : ")
    result = await agent.run(task=f"{stock_name}")
    print("Agent completed the task.")

    # Extract and print only the content from TextMessage responses
    for message in result.messages:
        if isinstance(message, TextMessage):
            print(f"Analysis:\n{message.content}")
            print("-" * 50)  # Separator line


if __name__ == "__main__":
    asyncio.run(main())
