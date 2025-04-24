import json
import re

def parse_json_to_dict(json_data):
    """
    Parses any JSON string into a Python dictionary.
    It handles markdown blocks, escaped strings, and extracts JSON from noisy input.

    Parameters:
        json_data (str): A string that includes JSON data.

    Returns:
        dict: Parsed JSON as a Python dictionary.

    Raises:
        ValueError: If parsing fails with a detailed error message.
    """
    # Try direct parsing
    try:
        return json.loads(json_data)
    except json.JSONDecodeError:
        pass

    # Try markdown-style block cleanup
    cleaned = re.sub(r"^```(?:json)?\s*|```$", "", json_data.strip(), flags=re.IGNORECASE).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Try to extract a valid JSON block from noisy input
    match = re.search(r'({.*?}|\[.*?])', json_data, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse extracted JSON block: {e}")

    raise ValueError("No valid JSON found in input")
