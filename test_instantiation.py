import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

try:
    model = genai.GenerativeModel("imagen-3.0-generate-001")
    response = model.generate_content("A drawing of a cat")
    print(f"Response type: {type(response)}")
    print(f"Response: {response}")
except Exception as e:
    print(f"Failed: {e}")
