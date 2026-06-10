"""Kiểm tra nhanh API key + model (chạy: python scripts/test_gemini_key.py)"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv()

import google.generativeai as genai

def main():
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        print("Missing GEMINI_API_KEY in .env")
        return 1

    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    genai.configure(api_key=key)
    print(f"Testing model: {model} ...")
    try:
        m = genai.GenerativeModel(model)
        r = m.generate_content("Reply with one word: OK")
        print("OK - API works:", (r.text or "").strip()[:80])
        return 0
    except Exception as e:
        print("FAIL:", e)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
