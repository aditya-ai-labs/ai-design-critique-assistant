import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

HF_API_KEY = os.getenv("HF_API_KEY")