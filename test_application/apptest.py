import google.generativeai as genai
import os
import PIL.Image
from dotenv import load_dotenv
load_dotenv()

genai.configure(api_key=os.environ["API_KEY"])

model = genai.GenerativeModel("gemini-1.5-flash")
ss = PIL.Image.open("uploads/uploaded_image.jpg")
prompt = "I am giving you a screenshot of an app. Output should describe a detailed, step-by-step guide on how to test each functionality. Each test case should include: Description: What the test case is about. Pre-conditions: What needs to be set up or ensured before testing. Testing Steps: Clear, step-by-step instructions on how to perform the test. Expected Result: What should happen if the feature works correctly."

response = model.generate_content([prompt, ss])
print(response.text)