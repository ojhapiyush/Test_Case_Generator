from flask import Flask, render_template, request, redirect, url_for
import os
from PIL import Image
import google.generativeai as genai
from dotenv import load_dotenv
import PIL.Image
import markdown

load_dotenv()
genai.configure(api_key=os.getenv("API_KEY"))

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part"
    
    file = request.files['file']

    if file.filename == '':
        return "No selected file"

    if file and allowed_file(file.filename):
        filename = os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded_image.jpg')
        try:
            file.save(filename)
            model = genai.GenerativeModel("gemini-1.5-flash")
            promptin = (
                "I am providing you with a screenshot of an application. Based on this, generate a well-structured "
                "and comprehensive testing guide that details how to test each functionality of the app. Each test case "
                "should be clear and easy to follow, ensuring it's formatted neatly for web presentation. For each functionality, "
                "provide:\n\n"
                "- **Description:** A concise overview of what the test case is intended to verify.\n"
                "- **Pre-conditions:** A list of any prerequisites or conditions that must be met before performing the test "
                "(e.g., user logged in, specific settings applied).\n"
                "- **Testing Steps:** A numbered, step-by-step set of instructions outlining how to conduct the test.\n"
                "- **Expected Result:** A description of what should happen if the feature or functionality behaves as expected.\n\n"
                "Ensure that the output is well-formatted, making it easy to read and visually appealing when displayed on a webpage, "
                "with clear headings and organized sections. Use bullet points, numbered lists, and bold text to highlight important information. Use HTML tags that are used inside BODY tags for formatting and do not use any markdown syntax. "
            )
            ss = PIL.Image.open("uploads/uploaded_image.jpg")
            response = model.generate_content([promptin,ss])
            html_content = markdown.markdown(response.text)
            return render_template('result.html', result=html_content)
        except Exception as e:
            print(f"Error occurred: {str(e)}")
            return "An error occurred while processing the image or API call"
    return "File upload failed"
if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
