import os
import google.generativeai as genai
from dotenv import load_dotenv

# Tải API key từ file .env
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

print("🔍 Đang truy vấn danh sách các model Google cho phép bạn dùng...")
print("-" * 50)

# Lọc và in ra các model hỗ trợ tạo văn bản (generateContent)
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)
        
print("-" * 50)