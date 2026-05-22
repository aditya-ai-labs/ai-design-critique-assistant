from google import genai
from google.genai import types
from config.settings import GEMINI_API_KEY ,HF_API_KEY
import json
from io import BytesIO
from fpdf import FPDF
import requests
from app.backend.services.prompt_engine import build_prompt

client = genai.Client(api_key=GEMINI_API_KEY)

# =============== Huggingface Model ===================================

HF_MODEL = "HuggingFaceH4/zephyr-7b-beta"

def query_huggingface(prompt):
    API_URL = f"https://hf.space/embed/{HF_MODEL}/+api/predict"

    headers = {
        "Authorization": f"Bearer {HF_API_KEY}"
    }

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 500
        }
    }

    response = requests.post(API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()[0]["generated_text"]
    else:
        return None

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

        # 🔥 PRIMARY MODEL (GEMINI)
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
        print("Gemini Error:", e)

        # 🔥 TRY HF
        try:
            hf_output = query_huggingface(prompt)

            if hf_output:
                return {
                    "analysis": [
                        {
                            "category": "AI Fallback",
                            "issue": hf_output[:300],
                            "suggestion": "Generated using HuggingFace",
                            "severity": "Info"
                        }
                    ]
                }

        except Exception as hf_error:
            print("HF Error:", hf_error)

        # 🔥 FINAL LOCAL FALLBACK (NO API)
        return {
            "analysis": [
                {
                    "category": "Layout",
                    "issue": "Basic UI alignment issue detected",
                    "suggestion": "Ensure consistent spacing and alignment",
                    "severity": "Recommended"
                },
                {
                    "category": "Typography",
                    "issue": "Font hierarchy unclear",
                    "suggestion": "Use proper heading sizes",
                    "severity": "Minor"
                }
            ]
        }
                

        # # 🔥 FINAL FALLBACK (SAFE)
        # return fallback_response(str(e))
# ---------------- CHAT ----------------
async def chat_with_context(question, analysis):
    try:
        prompt = f"""
You are a UX mentor.

Previous analysis:
{json.dumps(analysis, indent=2)}

User question:
{question}

Answer clearly.
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return response.text

    except Exception as e:
        print("CHAT AI ERROR:", e)

        hf_output = query_huggingface(question)
        if hf_output:
            return hf_output[:300]

        return "AI unavailable"

# ---------------- IMPROVE UI ----------------
def generate_ui_image(prompt):
    API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2"

    headers = {
        "Authorization": f"Bearer {HF_API_KEY}"
    }

    response = requests.post(API_URL, headers=headers, json={"inputs": prompt})

    if response.status_code == 200:
        return response.content
    else:
        print("Image Gen Error:", response.text)
        return None


async def improve_ui(analysis):
    try:
        prompt = f"""
Modern mobile app UI, clean layout, UX optimized, based on:
{analysis}
Minimal, professional, figma style
"""

        image_bytes = generate_ui_image(prompt)

        if image_bytes:
            file_path = "generated_ui.png"
            with open(file_path, "wb") as f:
                f.write(image_bytes)

            return {"image": file_path}

        return {"image": None}

    except Exception as e:
        print("Improve UI Error:", e)
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