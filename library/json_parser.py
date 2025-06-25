import json
import re


def parse_json_to_dict(json_data):
    """
    Parses a JSON string into a Python dictionary.
    - Strips markdown-style code block wrappers (e.g. ```json)
    - Replaces all newlines with spaces
    - Handles unescaped backslashes cautiously
    - Returns a valid Python dictionary or raises JSONDecodeError if invalid
    """
    # Remove markdown-style code block wrappers
    cleaned = re.sub(r'^```(?:json)?\s*|\s*```$', '', json_data.strip(), flags=re.IGNORECASE)

    # Normalize newlines to spaces
    cleaned = re.sub(r'[\r\n]+', ' ', cleaned)

    # Carefully escape unescaped backslashes that aren't part of valid sequences
    # Valid sequences: \", \\, \/, \b, \f, \n, \r, \t, \uXXXX
    cleaned = re.sub(r'(?<!\\)\\(?!["\\/bfnrtu])', r'\\\\', cleaned)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        # Optional: print debug info or raise the error
        print(f"Failed to decode JSON: {e}")
        print("Cleaned JSON string:", repr(cleaned))
        return None
