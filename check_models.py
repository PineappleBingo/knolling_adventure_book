import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("Error: GOOGLE_API_KEY not found.")
else:
    genai.configure(api_key=api_key)
    print("Available Models:")
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"Content: {m.name}")
            if 'generateImages' in m.supported_generation_methods: # Check for image generation support too
                print(f"Image: {m.name}")
    except Exception as e:
        print(f"Error listing models: {e}")

    print("\nChecking ImageGenerationModel availability:")
    try:
        print(f"genai.ImageGenerationModel: {genai.ImageGenerationModel}")
    except AttributeError:
        print("genai.ImageGenerationModel does not exist in this version.")
