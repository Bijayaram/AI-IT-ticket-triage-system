import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
print(f"Testing with key: {api_key[:15]}...")

try:
    genai.configure(api_key=api_key)
    
    # List available models
    print("\nAvailable models:")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"  - {m.name}")
    
    print("\nTrying gemini-pro...")
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content("Say hello")
    print(f"SUCCESS: {response.text}")
    
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
