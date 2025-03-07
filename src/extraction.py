import re
import pdfplumber
import docx2txt
from PIL import Image
import pytesseract
import fitz  
from bs4 import BeautifulSoup

def extract_text_from_pdf(file_path):
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error extracting PDF text with pdfplumber: {e}")
    return text

def extract_text_from_docx(file_path):
    try:
        return docx2txt.process(file_path)
    except Exception as e:
        print(f"Error extracting DOCX text: {e}")
        return ""

def extract_text_from_txt(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"Error reading TXT file: {e}")
        return ""

def ocr_image(file_path):
    try:
        img = Image.open(file_path)
        return pytesseract.image_to_string(img)
    except Exception as e:
        print(f"Error in OCR: {e}")
        return ""

def sanitize_text(text):
    return text.replace('\x00', '')

def extract_html_from_pdf(file_path):
    """Trích xuất nội dung PDF dưới dạng HTML bằng PyMuPDF."""
    html = ""
    try:
        doc = fitz.open(file_path)
        for page in doc:
            html += page.get_text("html")
    except Exception as e:
        print(f"Error extracting HTML from PDF: {e}")
    return html

def extract_text(file_path, extension):
    if extension.lower() == "pdf":
        html_text = extract_html_from_pdf(file_path)
        if html_text.strip():
            return sanitize_text(html_text).lower()
        else:
            text = extract_text_from_pdf(file_path)
            if not text.strip():
                text = ocr_image(file_path)
            return sanitize_text(text).lower()
    elif extension.lower() == "docx":
        text = extract_text_from_docx(file_path)
        return sanitize_text(text).lower()
    elif extension.lower() == "txt":
        text = extract_text_from_txt(file_path)
        return sanitize_text(text).lower()
    elif extension.lower() in ["png", "jpg", "jpeg"]:
        text = ocr_image(file_path)
        return sanitize_text(text).lower()
    else:
        return ""

def parse_html_sections(html_text):
    soup = BeautifulSoup(html_text, "html.parser")
    result = {}
    h1 = soup.find("h1")
    if h1:
        result["full name"] = h1.get_text(strip=True)
    for h2 in soup.find_all("h2"):
        field = h2.get_text(strip=True).lower()
        content_parts = []
        sibling = h2.find_next_sibling()
        while sibling and sibling.name not in ["h1", "h2"]:
            content_parts.append(sibling.get_text(strip=True))
            sibling = sibling.find_next_sibling()
        result[field] = "\n".join(content_parts)
    return result

def extract_candidate_info_with_tags(file_path):
    html_text = extract_html_from_pdf(file_path)
    html_text = sanitize_text(html_text).lower()
    sections = parse_html_sections(html_text)
    mapping = {
        "full name": "full_name",
        "phone": "phone",
        "email": "email",
        "address": "address",
        "education": "education",
        "experience": "experience",
        "certifications": "certifications",
        "skills": "skills"
    }
    info = {}
    for key, new_key in mapping.items():
        info[new_key] = sections.get(key, "")
    info["raw_text"] = html_text
    return info

def extract_section_by_synonyms(text, header_synonyms, stop_synonyms):
    lines = text.splitlines()
    section_lines = []
    capture = False
    header_regex = r"^(" + "|".join(header_synonyms) + r")\s*[:\-]?\s*(.*)"
    header_pattern = re.compile(header_regex, re.IGNORECASE)
    stop_regex = r"^(" + "|".join(stop_synonyms) + r")\s*[:\-]?"
    stop_pattern = re.compile(stop_regex, re.IGNORECASE)
    for line in lines:
        match = header_pattern.match(line.strip())
        if match:
            capture = True
            if match.group(2):
                section_lines.append(match.group(2).strip())
            continue
        if capture:
            if stop_pattern.match(line.strip()):
                break
            section_lines.append(line.strip())
    return "\n".join(section_lines).strip()

def extract_name(text):
    """
    Giả định tên ứng viên nằm ở vài dòng đầu của CV.
    Loại bỏ các dòng chứa từ khóa như dob, gender, phone, email, address.
    Trả về dòng đầu tiên có từ 2 đến 5 từ.
    """
    lines = text.splitlines()
    for line in lines[:5]:
        if not re.search(r"(dob|gender|phone|email|address)", line, re.IGNORECASE):
            words = line.strip().split()
            if 2 <= len(words) <= 5:
                return line.strip()
    return "unknown"

def extract_phone(text):
    phone_pattern = re.compile(r'(?:(?:\+?84)|0)(?:\s*\d){9,10}')
    match = phone_pattern.search(text)
    return match.group().strip() if match else ""

def extract_email(text):
    email_pattern = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+')
    match = email_pattern.search(text)
    return match.group().strip() if match else ""

def extract_address(text):
    addr_pattern = re.compile(r"(address|địa chỉ)\s*[:\-]\s*(.*)", re.IGNORECASE)
    for line in text.splitlines():
        match = addr_pattern.search(line)
        if match:
            return match.group(2).strip()
    return ""

def extract_candidate_info(text):
    if "<h1" in text and "<h2" in text:
        return parse_html_sections(text)
    section_synonyms = {
        "education": ["education", "academic", "edu"],
        "experience": ["work experience", "experience", "career", "professional experience"],
        "certifications": ["certifications", "certificates", "licenses", "chứng chỉ"],
        "skills": ["skills", "technical skills", "expertise", "proficiency", "kỹ năng"]
    }
    common_stop = ["objective", "contact", "interests", "activities", "personal", "summary", "profile"]
    info = {}
    info["full_name"] = extract_name(text)
    info["phone"] = extract_phone(text)
    info["email"] = extract_email(text)
    info["address"] = extract_address(text)
    info["education"] = extract_section_by_synonyms(text, section_synonyms["education"],
                                                     section_synonyms["experience"] + section_synonyms["certifications"] + section_synonyms["skills"] + common_stop)
    info["experience"] = extract_section_by_synonyms(text, section_synonyms["experience"],
                                                      section_synonyms["education"] + section_synonyms["certifications"] + section_synonyms["skills"] + common_stop)
    info["certifications"] = extract_section_by_synonyms(text, section_synonyms["certifications"],
                                                          section_synonyms["education"] + section_synonyms["experience"] + section_synonyms["skills"] + common_stop)
    info["skills"] = extract_section_by_synonyms(text, section_synonyms["skills"],
                                                  section_synonyms["education"] + section_synonyms["experience"] + section_synonyms["certifications"] + common_stop)
    info["raw_text"] = text
    return info
