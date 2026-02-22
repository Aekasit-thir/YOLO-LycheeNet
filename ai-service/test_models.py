import warnings
warnings.filterwarnings('ignore', category=FutureWarning)

import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# ตรวจสอบ API Key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ GEMINI_API_KEY not found!")
    exit(1)

print(f"✅ API Key found: {api_key[:10]}...")

genai.configure(api_key=api_key)

print("\n📋 Available models that support generateContent:\n")
try:
    models = genai.list_models()
    found = False
    for model in models:
        if 'generateContent' in model.supported_generation_methods:
            print(f"✅ {model.name}")
            found = True
    
    if not found:
        print("❌ No models found!")
        
except Exception as e:
    print(f"❌ Error listing models: {e}")
    print("\nTrying alternative method...")
    
    # ลอง models ที่น่าจะใช้ได้
    test_models = [
        'gemini-pro',
        'gemini-pro-vision',
        'gemini-1.5-flash',
        'gemini-1.5-pro',
        'models/gemini-pro',
        'models/gemini-pro-vision'
    ]
    
    for model_name in test_models:
        try:
            model = genai.GenerativeModel(model_name=model_name)
            print(f"✅ {model_name} - Available")
        except Exception as e:
            print(f"❌ {model_name} - Not available")