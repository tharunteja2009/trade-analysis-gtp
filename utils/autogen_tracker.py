"""
AutoGen Chat Wrapper with Token Tracking
Wraps AutoGen functionality to track token consumption and costs
"""

from typing import Any, Dict, List, Optional
from utils.cost_tracker import track_usage
import re


def estimate_tokens(text: str) -> int:
    """
    Rough estimation of tokens in text
    Generally, 1 token ≈ 4 characters for English text
    This is used when exact token counts aren't available
    """
    return len(text) // 4


def track_manual_usage(prompt: str, response: str, model_name: str = "gpt-4o"):
    """
    Manually track token usage when exact counts aren't available
    Uses estimation based on text length
    """
    prompt_tokens = estimate_tokens(prompt)
    completion_tokens = estimate_tokens(response)

    track_usage(model_name, prompt_tokens, completion_tokens)

    return {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": prompt_tokens + completion_tokens,
        "estimated": True,
    }


class AutoGenTeamTracker:
    """Track token usage for AutoGen team conversations"""

    def __init__(self, team_name: str = "stock_analysis_team"):
        self.team_name = team_name
        self.conversation_history = []

    def track_message(
        self, agent_name: str, message_content: str, model_name: str = "gpt-4o"
    ):
        """Track a message in the team conversation"""

        # Estimate tokens for the message
        estimated_tokens = estimate_tokens(message_content)

        # For team conversations, we estimate that:
        # - User/input messages count as prompt tokens
        # - Agent responses count as completion tokens
        if agent_name.lower() in ["user", "human", "input"]:
            track_usage(model_name, estimated_tokens, 0)
        else:
            track_usage(model_name, 0, estimated_tokens)

        # Store conversation history
        self.conversation_history.append(
            {
                "agent": agent_name,
                "message": message_content,
                "estimated_tokens": estimated_tokens,
                "model": model_name,
            }
        )

    def track_conversation_result(self, result, model_name: str = "gpt-4o"):
        """Track the entire conversation result from AutoGen"""
        if hasattr(result, "messages"):
            for message in result.messages:
                agent_name = getattr(message, "source", "unknown")
                content = str(getattr(message, "content", ""))
                self.track_message(agent_name, content, model_name)
        elif isinstance(result, list):
            # Handle list of messages
            for i, message in enumerate(result):
                if hasattr(message, "source"):
                    agent_name = message.source
                    content = str(message.content)
                elif hasattr(message, "role"):
                    agent_name = message.role
                    content = str(getattr(message, "content", ""))
                else:
                    agent_name = f"agent_{i}"
                    content = str(message)

                self.track_message(agent_name, content, model_name)

    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get summary of the conversation"""
        total_tokens = sum(msg["estimated_tokens"] for msg in self.conversation_history)

        agent_breakdown = {}
        for msg in self.conversation_history:
            agent = msg["agent"]
            if agent not in agent_breakdown:
                agent_breakdown[agent] = {"messages": 0, "tokens": 0}
            agent_breakdown[agent]["messages"] += 1
            agent_breakdown[agent]["tokens"] += msg["estimated_tokens"]

        return {
            "team_name": self.team_name,
            "total_messages": len(self.conversation_history),
            "total_estimated_tokens": total_tokens,
            "agent_breakdown": agent_breakdown,
        }


# Global team tracker
team_tracker = AutoGenTeamTracker()


def track_team_message(
    agent_name: str, message_content: str, model_name: str = "gpt-4o"
):
    """Convenience function to track team messages"""
    team_tracker.track_message(agent_name, message_content, model_name)


def track_autogen_result(result, model_name: str = "gpt-4o"):
    """Track the result from AutoGen team conversation"""
    team_tracker.track_conversation_result(result, model_name)


def get_team_summary() -> Dict[str, Any]:
    """Get team conversation summary"""
    return team_tracker.get_conversation_summary()


def format_team_summary(summary: Dict[str, Any]) -> str:
    """Format team summary for display"""
    if not summary:
        return "No team conversation data available."

    result = f"""
🤖 TEAM CONVERSATION SUMMARY
{'='*40}
Team: {summary.get('team_name', 'Unknown')}
Total Messages: {summary.get('total_messages', 0)}
Estimated Tokens: {summary.get('total_estimated_tokens', 0):,}

Agent Breakdown:
"""

    for agent, data in summary.get("agent_breakdown", {}).items():
        result += (
            f"  • {agent}: {data['messages']} messages, {data['tokens']:,} tokens\n"
        )

    result += "=" * 40
    return result


def parse_stock_data_for_tracking(stock_data: str) -> Dict[str, int]:
    """
    Parse stock data string to estimate tokens used in data collection
    """
    # Estimate tokens for different sections
    sections = {"basic_info": 0, "fundamentals": 0, "financials": 0, "company_info": 0}

    # Basic pattern matching for different data sections
    if "Current Price" in stock_data:
        sections["basic_info"] = estimate_tokens(
            stock_data.split("Fundamentals")[0]
            if "Fundamentals" in stock_data
            else stock_data[:500]
        )

    if "Market Cap" in stock_data:
        fundamentals_text = ""
        if "Fundamentals" in stock_data and "Company Info" in stock_data:
            fundamentals_text = stock_data.split("Fundamentals")[1].split(
                "Company Info"
            )[0]
        elif "Fundamentals" in stock_data:
            fundamentals_text = stock_data.split("Fundamentals")[1][:1000]
        sections["fundamentals"] = estimate_tokens(fundamentals_text)

    if "Income Statement" in stock_data or "Balance Sheet" in stock_data:
        financial_sections = ["Income Statement", "Balance Sheet", "Cash Flow"]
        financial_text = ""
        for section in financial_sections:
            if section in stock_data:
                financial_text += section + " data found; "
        sections["financials"] = estimate_tokens(
            financial_text + str(len(stock_data) // 2)
        )  # Financials are usually large

    if "Company Info" in stock_data:
        company_text = ""
        if "Company Info" in stock_data and "Financials" in stock_data:
            company_text = stock_data.split("Company Info")[1].split("Financials")[0]
        elif "Company Info" in stock_data:
            company_text = stock_data.split("Company Info")[1][:1000]
        sections["company_info"] = estimate_tokens(company_text)

    return sections
