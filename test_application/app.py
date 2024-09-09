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
    file2 = request.files.get('file2')  
    file3 = request.files.get('file3')      
    prompt_by_user = request.form['description']
    if len(prompt_by_user) != 0:
        additional_prompt = "Take care of these conditions specially: " + prompt_by_user
    else:
        additional_prompt = ""

    if file.filename == '':
        return "No selected file"

    if file and allowed_file(file.filename):
        filename = os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded_image.jpg')
        try:
            file.save(filename)
            
            model = genai.GenerativeModel("gemini-1.5-flash")
            promptin = (
                "Based on the screenshot provided understand the userflow and then generate a well-structured "
                "and comprehensive testing guide that details how to test each functionality of the app. For each functionality, "
                "provide:\n\n"
                "- **Description:** A concise overview of what the test case is intended to verify.\n"
                "- **Pre-conditions:** A list of any prerequisites or conditions that must be met before performing the test "
                "(e.g., user logged in, specific settings applied).\n"
                "- **Testing Steps:** A numbered, step-by-step set of instructions outlining how to conduct the test.\n"
                "- **Expected Result:** A description of what should happen if the feature or functionality behaves as expected.\n\n"
                "Ensure that the output is well-formatted, making it easy to read and visually appealing when displayed on a webpage, "
                "with clear headings and organized sections. Use bullet points, numbered lists, and bold text to highlight important information. Only use the most important section of the screenshot"
                + additional_prompt
            )
            prompt_to_model = [promptin]
            ss = PIL.Image.open("uploads/uploaded_image.jpg")
            prompt_to_model.append(ss)
            
            if file2 and allowed_file(file2.filename):
                filename2 = os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded_image2.jpg')
                file2.save(filename2)
                ss2 = PIL.Image.open("uploads/uploaded_image2.jpg")
                prompt_to_model.append(ss2)

            if file3 and allowed_file(file3.filename):
                filename3 = os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded_image3.jpg')
                file3.save(filename3)
                ss3 = PIL.Image.open("uploads/uploaded_image3.jpg")
                prompt_to_model.append(ss3)

            response = model.generate_content(prompt_to_model)
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
