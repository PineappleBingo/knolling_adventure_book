import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model_name = "models/gemini-2.0-flash-exp-image-generation"
print(f"Testing {model_name}...")

try:
    model = genai.GenerativeModel(model_name)
    response = model.generate_content("Draw a cute robot firefighter")
    print(f"Response: {response}")
    if response.parts:
        print("Parts found.")
        for part in response.parts:
            print(f"Part mime_type: {part.mime_type}")
except Exception as e:
    print(f"Failed: {e}")
