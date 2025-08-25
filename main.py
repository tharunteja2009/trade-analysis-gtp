from ai.models.gtp_model_client import get_openai_client
from ai.agents.trade_analysis_agent import get_trade_analyst_agent
import asyncio


async def main():
    # Example usage of the get_openai_client function
    model_strategy = (
        "economic-task"  # This can be changed to "deapth-analysis" as needed
    )
    client = get_openai_client(model_strategy)
    print(f"Initialized model for strategy: {model_strategy}")
    agent = get_trade_analyst_agent(model_strategy)
    result = await agent.run(task="tell about pfc stock")
    print(f"Agent response: \n {result}")


if __name__ == "__main__":
    asyncio.run(main())
