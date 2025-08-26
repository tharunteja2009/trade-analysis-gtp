"""
Utility functions for formatting numbers in readable format
"""

import ast


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
                    formatted_dict[key] = value
            else:
                formatted_dict[key] = value
        return formatted_dict
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
        except:
            pass

    return data
