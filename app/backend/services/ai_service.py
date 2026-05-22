from google import genai
from google.genai import types
from config.settings import GEMINI_API_KEY
import json
from io import BytesIO
from fpdf import FPDF
import requests
from app.backend.services.prompt_engine import build_prompt

client = genai.Client(api_key=GEMINI_API_KEY)

# ---------------- ANALYZE UI ----------------
async def analyze_ui(file):
    try:
        image_bytes = await file.read()

        # 🔥 SAFE MIME DETECTION
        filename = file.filename.lower()
        if filename.endswith(".jpg") or filename.endswith(".jpeg"):
            mime_type = "image/jpeg"
        elif filename.endswith(".png"):
            mime_type = "image/png"
        else:
            mime_type = "image/png"

        prompt = build_prompt()

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                prompt,
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type=mime_type
                )
            ]
        )

        text = response.text.strip()

        # 🔥 CLEAN JSON
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]

        result = json.loads(text)

        return result

    except Exception as e:
        print("ERROR (analyze):", e)

        # 🔥 HANDLE QUOTA ERROR
        if "429" in str(e):
            return {
                "analysis": [
                    {
                        "category": "System",
                        "issue": "API quota exceeded",
                        "suggestion": "Wait for a minute or reduce usage",
                        "severity": "Info"
                    }
                ]
            }

        return fallback_response(str(e))


# ---------------- CHAT ----------------
async def chat_with_context(question, analysis):
    try:
        # 🔥 Reduce token usage (IMPORTANT)
        short_analysis = json.dumps(analysis)[:1000]

        prompt = f"""
You are a UX mentor.

UI Analysis:
{short_analysis}

User Question:
{question}

Give short and helpful answer.
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return response.text

    except Exception as e:
        print("ERROR (chat):", e)

        if "429" in str(e):
            return "⚠️ API limit reached. Please wait."

        return f"Error: {str(e)}"


# ---------------- IMPROVE UI ----------------
async def improve_ui(analysis):
    try:
        # 🔥 No API call (save quota)
        return {
            "image": "https://dummyimage.com/600x400/000/fff&text=Improved+UI"
        }

    except Exception as e:
        return {"image": None}


# ---------------- EXPORT PDF ----------------
def export_pdf(analysis, image_url):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, "AI Design Report", ln=True)

    for item in analysis:
        pdf.multi_cell(0, 10, f"""
Category: {item.get('category')}
Issue: {item.get('issue')}
Suggestion: {item.get('suggestion')}
""")

    # 🔥 SAFE IMAGE ADD
    if image_url:
        try:
            img_data = requests.get(image_url).content
            with open("temp.png", "wb") as f:
                f.write(img_data)
            pdf.image("temp.png", x=10, w=100)
        except:
            pass

    # 🔥 FIXED OUTPUT
    pdf_bytes = pdf.output(dest='S').encode('latin-1')
    return BytesIO(pdf_bytes)


# ---------------- FALLBACK ----------------
def fallback_response(error_msg):
    return {
        "analysis": [
            {
                "category": "System",
                "issue": "Processing failed",
                "suggestion": error_msg,
                "severity": "Critical"
            }
        ]
    }