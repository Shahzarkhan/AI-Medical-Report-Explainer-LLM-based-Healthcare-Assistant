import json
import re

def extract_json(ai_response):
    """
    Extracts JSON data from the AI response string.
    """
    try:
        # json detect the block.
        match = re.search(r'\{.*\}', ai_response, re.DOTALL)
        if match:
            json_text = match.group()
            return json.loads(json_text)
    
    except Exception as e:
        print("JSON Parsing Error:", e)
    return None