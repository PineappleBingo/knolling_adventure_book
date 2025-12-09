import google.generativeai as genai
import pprint
import sys

print("Python version:", sys.version)
print("genai version:", genai.__version__)

print("\n--- dir(genai) ---")
pprint.pprint(dir(genai))

print("\n--- Attempting direct import ---")
try:
    from google.generativeai import ImageGenerationModel
    print("SUCCESS: from google.generativeai import ImageGenerationModel works!")
except ImportError as e:
    print(f"FAILURE: from google.generativeai import ImageGenerationModel failed: {e}")

try:
    model = genai.ImageGenerationModel("imagen-3.0-generate-001")
    print("SUCCESS: genai.ImageGenerationModel instantiated!")
except AttributeError:
    print("FAILURE: genai.ImageGenerationModel does not exist.")
except Exception as e:
    print(f"FAILURE: Instantiation error: {e}")
