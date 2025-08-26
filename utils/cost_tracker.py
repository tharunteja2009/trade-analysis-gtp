"""
Token and Cost Tracking Utility for AI-Powered Stock Analysis
Tracks token consumption and costs for AutoGen agents and LLM calls
"""

import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class TokenUsage:
    """Track token usage for a single request"""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    model_name: str = ""
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def cost_usd(self) -> float:
        """Calculate cost in USD based on model pricing"""
        return calculate_cost(
            self.model_name, self.prompt_tokens, self.completion_tokens
        )


@dataclass
class SessionCosts:
    """Track costs for an entire session"""

    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    token_usages: List[TokenUsage] = field(default_factory=list)
    stock_symbol: str = ""
    app_type: str = ""  # "console" or "streamlit"

    @property
    def total_prompt_tokens(self) -> int:
        return sum(usage.prompt_tokens for usage in self.token_usages)

    @property
    def total_completion_tokens(self) -> int:
        return sum(usage.completion_tokens for usage in self.token_usages)

    @property
    def total_tokens(self) -> int:
        return sum(usage.total_tokens for usage in self.token_usages)

    @property
    def total_cost_usd(self) -> float:
        return sum(usage.cost_usd for usage in self.token_usages)

    @property
    def duration_seconds(self) -> float:
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return (datetime.now() - self.start_time).total_seconds()


class CostTracker:
    """Main cost tracking class"""

    def __init__(self):
        self.current_session: Optional[SessionCosts] = None
        self.all_sessions: List[SessionCosts] = []

    def start_session(self, stock_symbol: str, app_type: str = "console") -> str:
        """Start a new tracking session"""
        session_id = f"{app_type}_{stock_symbol}_{int(time.time())}"
        self.current_session = SessionCosts(
            session_id=session_id,
            start_time=datetime.now(),
            stock_symbol=stock_symbol,
            app_type=app_type,
        )
        return session_id

    def end_session(self):
        """End the current session"""
        if self.current_session:
            self.current_session.end_time = datetime.now()
            self.all_sessions.append(self.current_session)
            self.current_session = None

    def track_tokens(self, model_name: str, prompt_tokens: int, completion_tokens: int):
        """Track token usage for the current session"""
        if not self.current_session:
            return

        usage = TokenUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            model_name=model_name,
            timestamp=datetime.now(),
        )
        self.current_session.token_usages.append(usage)

    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of current session"""
        if not self.current_session:
            return {}

        return {
            "session_id": self.current_session.session_id,
            "stock_symbol": self.current_session.stock_symbol,
            "app_type": self.current_session.app_type,
            "duration_seconds": self.current_session.duration_seconds,
            "total_prompt_tokens": self.current_session.total_prompt_tokens,
            "total_completion_tokens": self.current_session.total_completion_tokens,
            "total_tokens": self.current_session.total_tokens,
            "total_cost_usd": self.current_session.total_cost_usd,
            "number_of_requests": len(self.current_session.token_usages),
            "models_used": list(
                set(usage.model_name for usage in self.current_session.token_usages)
            ),
        }

    def get_all_sessions_summary(self) -> Dict[str, Any]:
        """Get summary of all sessions"""
        if not self.all_sessions:
            return {}

        total_cost = sum(session.total_cost_usd for session in self.all_sessions)
        total_tokens = sum(session.total_tokens for session in self.all_sessions)
        total_requests = sum(len(session.token_usages) for session in self.all_sessions)

        console_sessions = [s for s in self.all_sessions if s.app_type == "console"]
        streamlit_sessions = [s for s in self.all_sessions if s.app_type == "streamlit"]

        return {
            "total_sessions": len(self.all_sessions),
            "total_cost_usd": total_cost,
            "total_tokens": total_tokens,
            "total_requests": total_requests,
            "console_sessions": len(console_sessions),
            "streamlit_sessions": len(streamlit_sessions),
            "console_cost": sum(s.total_cost_usd for s in console_sessions),
            "streamlit_cost": sum(s.total_cost_usd for s in streamlit_sessions),
            "average_cost_per_session": (
                total_cost / len(self.all_sessions) if self.all_sessions else 0
            ),
            "average_tokens_per_session": (
                total_tokens / len(self.all_sessions) if self.all_sessions else 0
            ),
        }


def calculate_cost(
    model_name: str, prompt_tokens: int, completion_tokens: int
) -> float:
    """
    Calculate cost based on model pricing (as of 2024)
    Prices are per 1M tokens
    """

    # OpenAI GPT pricing (USD per 1M tokens)
    pricing = {
        "gpt-4o": {"input": 5.00, "output": 15.00},
        "gpt-4o-mini": {"input": 0.15, "output": 0.60},
        "gpt-4-turbo": {"input": 10.00, "output": 30.00},
        "gpt-4": {"input": 30.00, "output": 60.00},
        "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
        "gpt-3.5-turbo-instruct": {"input": 1.50, "output": 2.00},
        # Azure OpenAI (similar pricing)
        "azure-gpt-4": {"input": 30.00, "output": 60.00},
        "azure-gpt-35-turbo": {"input": 0.50, "output": 1.50},
        # Default fallback (GPT-4o pricing)
        "default": {"input": 5.00, "output": 15.00},
    }

    # Normalize model name
    model_key = model_name.lower()
    if model_key not in pricing:
        model_key = "default"

    # Calculate costs
    input_cost = (prompt_tokens / 1_000_000) * pricing[model_key]["input"]
    output_cost = (completion_tokens / 1_000_000) * pricing[model_key]["output"]

    return input_cost + output_cost


def format_cost_summary(summary: Dict[str, Any]) -> str:
    """Format cost summary for display"""
    if not summary:
        return "No usage data available."

    return f"""
💰 TOKEN USAGE & COST SUMMARY
{'='*50}
📊 Session Details:
   • Stock Symbol: {summary.get('stock_symbol', 'N/A')}
   • App Type: {summary.get('app_type', 'N/A').title()}
   • Duration: {summary.get('duration_seconds', 0):.1f} seconds
   • API Requests: {summary.get('number_of_requests', 0)}

🔢 Token Consumption:
   • Prompt Tokens: {summary.get('total_prompt_tokens', 0):,}
   • Completion Tokens: {summary.get('total_completion_tokens', 0):,}
   • Total Tokens: {summary.get('total_tokens', 0):,}

💵 Cost Analysis:
   • Total Cost: ${summary.get('total_cost_usd', 0):.4f} USD
   • Cost per Token: ${(summary.get('total_cost_usd', 0) / max(summary.get('total_tokens', 1), 1)):.6f} USD
   • Models Used: {', '.join(summary.get('models_used', []))}

📈 Efficiency Metrics:
   • Tokens per Second: {(summary.get('total_tokens', 0) / max(summary.get('duration_seconds', 1), 1)):.1f}
   • Cost per Second: ${(summary.get('total_cost_usd', 0) / max(summary.get('duration_seconds', 1), 1)):.4f} USD
{'='*50}
"""


def format_all_sessions_summary(summary: Dict[str, Any]) -> str:
    """Format summary of all sessions"""
    if not summary:
        return "No session data available."

    return f"""
📋 OVERALL USAGE STATISTICS
{'='*50}
📊 Session Overview:
   • Total Sessions: {summary.get('total_sessions', 0)}
   • Console Sessions: {summary.get('console_sessions', 0)}
   • Streamlit Sessions: {summary.get('streamlit_sessions', 0)}

💰 Total Costs:
   • Overall Cost: ${summary.get('total_cost_usd', 0):.4f} USD
   • Console App Cost: ${summary.get('console_cost', 0):.4f} USD
   • Streamlit App Cost: ${summary.get('streamlit_cost', 0):.4f} USD

📈 Averages:
   • Avg Cost/Session: ${summary.get('average_cost_per_session', 0):.4f} USD
   • Avg Tokens/Session: {summary.get('average_tokens_per_session', 0):,.0f}
   • Total Requests: {summary.get('total_requests', 0)}
   • Total Tokens: {summary.get('total_tokens', 0):,}
{'='*50}
"""


# Global cost tracker instance
cost_tracker = CostTracker()


def start_tracking(stock_symbol: str, app_type: str = "console") -> str:
    """Convenience function to start tracking"""
    return cost_tracker.start_session(stock_symbol, app_type)


def end_tracking():
    """Convenience function to end tracking"""
    cost_tracker.end_session()


def track_usage(model_name: str, prompt_tokens: int, completion_tokens: int):
    """Convenience function to track token usage"""
    cost_tracker.track_tokens(model_name, prompt_tokens, completion_tokens)


def get_session_summary() -> str:
    """Get formatted session summary"""
    summary = cost_tracker.get_session_summary()
    return format_cost_summary(summary)


def get_all_sessions_summary() -> str:
    """Get formatted summary of all sessions"""
    summary = cost_tracker.get_all_sessions_summary()
    return format_all_sessions_summary(summary)


def save_session_data(filepath: str = "session_costs.json"):
    """Save session data to file"""
    try:
        data = {
            "sessions": [
                {
                    "session_id": session.session_id,
                    "start_time": session.start_time.isoformat(),
                    "end_time": (
                        session.end_time.isoformat() if session.end_time else None
                    ),
                    "stock_symbol": session.stock_symbol,
                    "app_type": session.app_type,
                    "total_cost_usd": session.total_cost_usd,
                    "total_tokens": session.total_tokens,
                    "duration_seconds": session.duration_seconds,
                    "token_usages": [
                        {
                            "model_name": usage.model_name,
                            "prompt_tokens": usage.prompt_tokens,
                            "completion_tokens": usage.completion_tokens,
                            "total_tokens": usage.total_tokens,
                            "cost_usd": usage.cost_usd,
                            "timestamp": usage.timestamp.isoformat(),
                        }
                        for usage in session.token_usages
                    ],
                }
                for session in cost_tracker.all_sessions
            ]
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        return f"Session data saved to {filepath}"
    except Exception as e:
        return f"Error saving session data: {str(e)}"
