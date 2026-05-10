import google.generativeai as genai
from config.settings import GEMINI_API_KEY
import json

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")


async def analyze_ui(file):
    try:
        image_bytes = await file.read()

        prompt = """
You are a senior UX design mentor.

Analyze this UI image and return ONLY valid JSON.

Format:
[
  {
    "category": "",
    "issue": "",
    "reason": "",
    "suggestion": "",
    "severity": "Critical/Recommended/Minor"
  }
]

Do not add text outside JSON.
"""

        response = model.generate_content([
            prompt,
            {"mime_type": "image/jpeg", "data": image_bytes}
        ])

        text_output = response.text

        return parse_response(text_output)

    except Exception as e:
        return fallback_response(str(e))
    


def parse_response(text):
    try:
        start = text.find("[")
        end = text.rfind("]") + 1

        json_str = text[start:end]

        return {"analysis": json.loads(json_str)}

    except:
        return fallback_response("JSON parsing failed")
    

def fallback_response(error_msg):
    return {
        "analysis": [
            {
                "category": "System",
                "issue": "Processing failed",
                "reason": error_msg,
                "suggestion": "Try again",
                "severity": "Critical"
            }
        ]
    }