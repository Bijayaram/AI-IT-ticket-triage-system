"""Quick test of Gemini API"""
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
print(f"API Key: {api_key[:20]}...")

# Test multiple model names
models_to_test = [
    "gemini-2.5-flash",
    "gemini-2.0-flash", 
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-pro"
]

genai.configure(api_key=api_key)

for model_name in models_to_test:
    try:
        print(f"\n[*] Testing: {model_name}")
        model = genai.GenerativeModel(model_name)
        
        response = model.generate_content("Say 'Hello' in JSON format: {\"message\": \"Hello\"}")
        print(f"[OK] {model_name} works!")
        print(f"Response: {response.text[:100]}")
        print(f"\n[SUCCESS] Use this model: {model_name}")
        break
        
    except Exception as e:
        error_msg = str(e)
        if "404" in error_msg or "not found" in error_msg:
            print(f"[ERROR] {model_name} not found")
        else:
            print(f"[ERROR] {model_name} failed: {error_msg[:100]}")
else:
    print("\n[FAILED] No working Gemini model found!")
