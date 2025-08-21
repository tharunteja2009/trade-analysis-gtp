from autogen_ext.models.openai import OpenAIChatCompletionClient
from os import getenv

# Initialize the OpenAIChatCompletionClient with the custom model
openai_api_key = getenv("OPENAI_API_KEY", "placeholder")


def get_openai_client(strategy_name: str):
    if strategy_name == "economic-task":
        model_info = {
            "model": "gpt-o3-mini",
            "vision": False,
            "function_calling": False,
            "json_output": False,
            "family": "gpt-o3",
            "structured_output": False,
        }
        return OpenAIChatCompletionClient(model="gpt-o3-mini", api_key=openai_api_key, model_info=model_info)
    elif strategy_name == "deapth-analysis":
        model_info = {
            "model": "gpt-o3-pro",
            "vision": False,
            "function_calling": False,
            "json_output": False,
            "family": "gpt-o3",
            "structured_output": False,
        }
        return OpenAIChatCompletionClient(model="gpt-o3-pro", api_key=openai_api_key, model_info=model_info)
