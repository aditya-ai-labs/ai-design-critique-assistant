from google import genai
from config.settings import GEMINI_API_KEY
from PIL import Image
import io
import json

client = genai.Client(api_key=GEMINI_API_KEY)


async def analyze_ui(file):
    try:
        image_bytes = await file.read()

        # ✅ convert to PIL image (CRITICAL FIX)
        image = Image.open(io.BytesIO(image_bytes))

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
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt, image]   # ✅ CORRECT FORMAT
        )

        text_output = response.text

        return parse_response(text_output)

    except Exception as e:
        return fallback_response(str(e))

# ---------------- CHAT ----------------
async def chat_with_context(question, analysis):
    try:
        prompt = f"""
You are a UX mentor.

Here is previous UI analysis:
{analysis}

User question:
{question}

Answer clearly and helpfully.
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return response.text

    except Exception as e:
        return f"Error: {str(e)}"


# ---------------- PARSER ----------------
def parse_response(text):
    try:
        start = text.find("[")
        end = text.rfind("]") + 1
        json_str = text[start:end]

        return {"analysis": json.loads(json_str)}

    except:
        return fallback_response("JSON parsing failed")


# ---------------- FALLBACK ----------------
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