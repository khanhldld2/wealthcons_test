import os
from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
from config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS
from src.extraction import extract_text, extract_candidate_info, extract_phone, extract_email, extract_address, extract_candidate_info_with_tags
from src.scoring import score_candidate, generate_interview_questions
from src.models import Candidate, init_db, SessionLocal

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

init_db()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "resume" not in request.files:
            return "No file part", 400
        file = request.files["resume"]
        if file.filename == "":
            return "No selected file", 400
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(file_path)
            extension = filename.rsplit(".", 1)[1].lower()
            text = extract_text(file_path, extension)

            if extension == "pdf" and "<h1" in text and "<h2" in text:
                info = extract_candidate_info_with_tags(file_path)
            else:
                info = extract_candidate_info(text)
            info["score"] = score_candidate(info)
            info["interview_questions"] = generate_interview_questions(info["raw_text"])

            db = SessionLocal()
            candidate = Candidate(
                full_name=info.get("full_name", "unknown"),
                phone=extract_phone(text),
                email=extract_email(text),
                linkedin="", 
                address=extract_address(text),
                education=info.get("education", ""),
                experience=info.get("experience", ""),
                certifications=info.get("certifications", ""),
                skills=info.get("skills", ""),
                score=info["score"],
                interview_questions=info["interview_questions"],
                raw_text=info["raw_text"]
            )
            db.add(candidate)
            db.commit()
            db.refresh(candidate)
            db.close()
            return render_template("result.html", candidate=candidate)
    return render_template("index.html")

def extract_phone(text):
    import re
    phone_pattern = re.compile(r'(?:(?:\+?84)|0)(?:\s*\d){9,10}')
    match = phone_pattern.search(text)
    return match.group().strip() if match else ""

def extract_email(text):
    import re
    email_pattern = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+')
    match = email_pattern.search(text)
    return match.group().strip() if match else ""

def extract_address(text):
    import re
    addr_pattern = re.compile(r"(address|địa chỉ)\s*[:\-]\s*(.*)", re.IGNORECASE)
    for line in text.splitlines():
        match = addr_pattern.search(line)
        if match:
            return match.group(2).strip()
    return ""

if __name__ == "__main__":
    app.run(debug=True)
