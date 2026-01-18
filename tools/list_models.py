import requests
import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv('GOOGLE_API_KEY')
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
response = requests.get(url)
print("--- AVAILABLE MODELS ---")
if response.status_code == 200:
    models = response.json().get('models', [])
    for m in models:
        if 'image' in m['name'] or 'imagen' in m['name']:
            print(f"FOUND: {m['name']}")
else:
    print(f"Error: {response.text}")
