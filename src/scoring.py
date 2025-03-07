import re
from transformers import pipeline

qg_pipeline = pipeline("text2text-generation", model="valhalla/t5-small-qg-prepend")

def calculate_experience_years(exp_text):
    pattern = re.compile(r'(\d+)\s*(years?|yrs?|months?)', re.IGNORECASE)
    matches = pattern.findall(exp_text)
    total = 0.0
    for num_str, unit in matches:
        try:
            num = float(num_str)
        except:
            num = 0
        if 'month' in unit.lower():
            total += num / 12.0
        else:
            total += num
    return int(total)

def score_candidate(info):
    score = 0
    exp_years = calculate_experience_years(info.get("experience", ""))
    score += exp_years * 2
    if info.get("education"):
        score += 10
    if info.get("skills"):
        skills_list = [s.strip() for s in re.split(r'[,;\n]', info["skills"]) if s.strip()]
        score += len(skills_list) * 5
    if info.get("certifications"):
        cert_list = [c.strip() for c in info["certifications"].splitlines() if c.strip()]
        score += len(cert_list) * 5
    return score

def generate_interview_questions(profile_text):
    prompt = (
        "Generate at least 5 advance personalized interview questions for this candidate based on the following experience profile:\n"
        f"{profile_text}\nQuestions:"
    )
    questions_text = qg_pipeline(prompt, max_length=300)[0]['generated_text']
    questions = [q.strip() for q in questions_text.split('\n') if q.strip()]
    return "\n".join(questions)
