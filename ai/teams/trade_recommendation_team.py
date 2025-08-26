from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.messages import TextMessage
from ai.agents.trade_data_collection_agent import get_trade_data_collection_agent
from ai.agents.trade_analysis_agent import get_trade_analyst_agent


def trade_recommendation_team():
    # Create agent instances, not function references
    data_agent = get_trade_data_collection_agent()  # This function takes no parameters
    analysis_agent = get_trade_analyst_agent()  # This function also takes no parameters

    team = RoundRobinGroupChat(
        participants=[data_agent, analysis_agent],
        max_turns=2,
    )
    return team
