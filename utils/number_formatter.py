"""
Utility functions for formatting numbers in readable format
"""

import ast
import pandas as pd


def format_large_number(value):
    """Convert large numbers to readable format (M for millions, B for billions, etc.)"""
    try:
        # Convert to float if it's a string representation of a number
        if isinstance(value, str):
            # Handle cases like "2.380800e+08" or "238080000"
            try:
                num = float(value)
            except ValueError:
                return value  # Return original if can't convert
        elif isinstance(value, (int, float)):
            num = float(value)
        else:
            return value  # Return original if not a number

        # Handle negative numbers
        negative = num < 0
        num = abs(num)

        # Define the formatting thresholds
        if num >= 1e12:  # Trillions
            formatted = f"{num/1e12:.2f}T"
        elif num >= 1e9:  # Billions
            formatted = f"{num/1e9:.2f}B"
        elif num >= 1e6:  # Millions
            formatted = f"{num/1e6:.2f}M"
        elif num >= 1e3:  # Thousands
            formatted = f"{num/1e3:.2f}K"
        else:
            # For smaller numbers, use regular formatting
            if num == int(num):
                formatted = f"{int(num):,}"
            else:
                formatted = f"{num:,.2f}"

        return f"-{formatted}" if negative else formatted

    except (ValueError, TypeError):
        return value  # Return original value if any error occurs


def format_data_for_console(data):
    """Format data with readable numbers for console display"""
    if isinstance(data, dict):
        formatted_dict = {}
        for key, value in data.items():
            if isinstance(value, dict):
                formatted_dict[key] = format_data_for_console(value)
            elif isinstance(value, pd.DataFrame):
                # Format DataFrame by applying number formatting to numeric columns
                formatted_df = value.copy()
                for col in formatted_df.columns:
                    if formatted_df[col].dtype in ["float64", "int64"]:
                        formatted_df[col] = formatted_df[col].apply(
                            lambda x: (
                                format_large_number(x)
                                if pd.notna(x) and abs(x) >= 1e6
                                else x
                            )
                        )
                formatted_dict[key] = formatted_df
            elif isinstance(value, (int, float)) and abs(value) >= 1e6:
                formatted_dict[key] = format_large_number(value)
            elif isinstance(value, str):
                try:
                    # Check if string represents a large number
                    num_value = float(value)
                    if abs(num_value) >= 1e6:
                        formatted_dict[key] = format_large_number(num_value)
                    else:
                        formatted_dict[key] = value
                except ValueError:
                    # Try to format numbers within the string
                    formatted_dict[key] = format_numbers_in_string(value)
            else:
                formatted_dict[key] = value
        return formatted_dict
    elif isinstance(data, pd.DataFrame):
        # Format DataFrame by applying number formatting to numeric columns
        formatted_df = data.copy()
        for col in formatted_df.columns:
            if formatted_df[col].dtype in ["float64", "int64"]:
                formatted_df[col] = formatted_df[col].apply(
                    lambda x: (
                        format_large_number(x) if pd.notna(x) and abs(x) >= 1e6 else x
                    )
                )
        return formatted_df
    elif isinstance(data, str):
        # Try to parse the string as a dictionary
        try:
            # Handle various string formats that might contain a dictionary
            data_str = str(data).strip()

            # Handle pprint format
            if data_str.startswith("(") and data_str.endswith(")"):
                data_str = data_str[1:-1].strip()

            if (data_str.startswith("'") and data_str.endswith("'")) or (
                data_str.startswith('"') and data_str.endswith('"')
            ):
                data_str = data_str[1:-1]

            # Try to parse as dictionary
            if data_str.strip().startswith("{") and data_str.strip().endswith("}"):
                parsed_data = ast.literal_eval(data_str)
                return format_data_for_console(parsed_data)
            else:
                # If it's just a string, try to format numbers within it
                return format_numbers_in_string(data_str)
        except:
            # If parsing fails, try to format numbers within the string
            return format_numbers_in_string(data)

    return data


def format_numbers_in_string(text):
    """Format large numbers found within a string"""
    import re

    # Pattern to match scientific notation numbers (e.g., 1.705100e+07, 2.530000e-01)
    scientific_pattern = r"(-?\d+\.?\d*e[+-]\d+)"

    def replace_scientific(match):
        try:
            num = float(match.group(1))
            if abs(num) >= 1e6:
                # Format large numbers with M/B/T
                return format_large_number(num)
            else:
                # For smaller numbers, convert to regular decimal format
                if abs(num) >= 1:
                    # For numbers >= 1, use appropriate decimal places
                    return f"{num:,.2f}".rstrip("0").rstrip(".")
                else:
                    # For numbers < 1, show more precision
                    formatted = f"{num:.6f}".rstrip("0").rstrip(".")
                    # If it's a very small number, keep at least 3 decimal places
                    if "." in formatted and len(formatted.split(".")[1]) < 3:
                        formatted = f"{num:.3f}"
                    return formatted
        except:
            return match.group(1)

    # Replace scientific notation numbers
    formatted_text = re.sub(scientific_pattern, replace_scientific, str(text))

    return formatted_text
