from autogen_ext.models.openai import OpenAIChatCompletionClient
import os
from dotenv import load_dotenv

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("Please set the OPENAI_API_KEY environment variable.")


def get_openai_client(strategy_name: str):
    if strategy_name == "economic-task":
        model_info = {
            "model": "gpt-4o-mini",
            "vision": False,
            "function_calling": True,
            "json_output": False,
            "family": "gpt-4o",
            "structured_output": False,
        }
        return OpenAIChatCompletionClient(
            model="gpt-4o-mini", api_key=openai_api_key, model_info=model_info
        )
    elif strategy_name == "deapth-analysis":
        model_info = {
            "model": "gpt-4o",
            "vision": False,
            "function_calling": True,
            "json_output": False,
            "family": "gpt-4o",
            "structured_output": False,
        }
        return OpenAIChatCompletionClient(
            model="gpt-4o", api_key=openai_api_key, model_info=model_info
        )
