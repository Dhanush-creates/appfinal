import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import PyPDF2

# Uncomment and configure your AI/LLM imports as needed
# import google.generativeai as genai

load_dotenv()
app = Flask(__name__, static_folder=".")
CORS(app)

# Configure Gemini API key if needed
# api_key = os.getenv("GEMINI_API_KEY")
# genai.configure(api_key=api_key)

def extract_pdf_text(file_stream):
    reader = PyPDF2.PdfReader(file_stream)
    full_text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            full_text += page_text + "\n"
    return full_text.strip()

def get_gemini_response(input_instruction, pdf_text, job_description):
    # Replace this with your actual AI call
    # model = genai.GenerativeModel('gemini-1.5-flash')
    # response = model.generate_content([input_instruction, pdf_text, job_description])
    # return response.text
    # For demo, just echo the input
    return f"<pre>Instruction: {input_instruction}\n\nResume (excerpt): {pdf_text[:200]}...\n\nJob Description: {job_description[:200]}...</pre>"

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    uploaded_file = request.files.get('resume')
    jobdesc = request.form.get('jobdesc', '')
    action = request.form.get('action', 'analyze')
    if not uploaded_file or not jobdesc:
        return jsonify({'result': 'Missing resume or job description.'})
    try:
        pdf_text = extract_pdf_text(uploaded_file.stream)
        if not pdf_text:
            return jsonify({'result': 'No readable text found in the uploaded PDF.'})
        if action == 'analyze':
            input_prompt = """
            You are an experienced technical human resource Manager. Your task is to review the provided resume against the job description.
            Please share your professional evaluation on whether the candidate's profile aligns with the role.
            Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
            """
        else:
            input_prompt = """
            You are a skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality.
            Your task is to evaluate the resume against the provided job description. Give me the percentage of match if the resume fits
            the job description. First the output should come as percentage, then keywords missing, and finally final thoughts.
            """
        result = get_gemini_response(input_prompt, pdf_text, jobdesc)
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'result': f'Error: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True)
