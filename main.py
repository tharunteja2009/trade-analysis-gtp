from ai.models.gtp_model_client import get_openai_client


def main():
    # Example usage of the get_openai_client function
    strategy_name = (
        "economic-task"  # This can be changed to "deapth-analysis" as needed
    )
    client = get_openai_client(strategy_name)
    print(f"Initialized client for strategy: {strategy_name}")


if __name__ == "__main__":
    main()
