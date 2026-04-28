"""Simple Gemini connectivity test."""

import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key or api_key == "your_gemini_api_key_here":
    raise SystemExit("Set GEMINI_API_KEY in your .env file before running this script.")

client = genai.Client(api_key=api_key)
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Say 'Gemini connection successful!'",
)
print(response.text)