from flask import Flask, request, jsonify, send_from_directory, render_template
import pdfplumber, docx, requests, json
from fpdf import FPDF
import re

app = Flask(__name__)
stored_resume_text = ""  # Stores resume in memory
ROADMAP_FILE = 'roadmap.pdf'

# ------------------ Groq API Setup ------------------
GROQ_API_KEY = ""  # Replace with your actual key
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama3-8b-8192"

HEADERS = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}

# ------------------ Groq Query ------------------
def query_groq(prompt):
    payload = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }

    try:
        response = requests.post(GROQ_URL, headers=HEADERS, json=payload, timeout=20)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        print("Groq Error:", e)
        return ""

# ------------------ Resume Text Extraction ------------------
def extract_text_from_resume(file):
    if file.filename.endswith('.pdf'):
        with pdfplumber.open(file) as pdf:
            return "\n".join([p.extract_text() for p in pdf.pages if p.extract_text()])
    elif file.filename.endswith('.docx'):
        doc = docx.Document(file)
        return "\n".join([p.text for p in doc.paragraphs])
    return ""

# ------------------ Extract Skills ------------------
def extract_skills(text):
    prompt = f"""
Extract a clean, comma-separated list of technical and soft skills from the following text.

Text:
{text[:3000]}

Only return the skills in this format:
Python, TensorFlow, Communication, Git, Teamwork
"""

    try:
        response = query_groq(prompt)
        print(" Skill Extracted Text:", response)

        # Filter response
        skills = [s.strip() for s in re.split(r',|\n', response) if s.strip()]
        # Remove known garbage
        garbage_phrases = [
            "Please provide the text", "I'll be happy to extract", "there is no text provided", "I apologize",
            "Technical skills:", "Soft skills:", "Here are the skills:", "Return", "None mentioned"
        ]
        skills = [s for s in skills if not any(phrase.lower() in s.lower() for phrase in garbage_phrases)]
        return skills
    except Exception as e:
        print("Skill extraction error:", e)
        return []



# ------------------ ATS Score ------------------
def get_ats_score(text):
    prompt = f"""
You're an Applicant Tracking System (ATS) assistant. Analyze the following resume and:

- Give an ATS Score out of 100
- Then list 3 improvement tips

Resume:
{text[:3500]}
"""

    try:
        response = query_groq(prompt)
        print(" Groq ATS raw response:", response)

        # Extract score more flexibly
        score_match = re.search(r'(\d{1,3})\s*(/100|out of 100)?', response, re.IGNORECASE)
        score = int(score_match.group(1)) if score_match else 0

        # Extract tips
        tips = re.findall(r'(?:\d+\.|\-)\s+(.*)', response)
        if not tips:
            tips = ["Add more measurable results.", "Include more keywords.", "Improve formatting."]

        return {
            "score": min(score, 100),
            "tips": tips[:3]
        }

    except Exception as e:
        print(" ATS Score parsing error:", e)
        return {
            "score": 0,
            "tips": [
                "Unable to parse score from response.",
                "Use simpler formatting in the resume.",
                "Ensure education and experience are listed clearly."
            ]
        }

# ------------------ Recommend Roles ------------------
def recommend_roles(text):
    prompt = f"""
Based on the following resume text, suggest the top 3 most relevant tech job roles.

Only return the roles in a comma-separated list format like:
Data Scientist, Backend Developer, ML Engineer

Resume:
{text[:3000]}
"""

    try:
        response = query_groq(prompt)
        print(" Raw role response:", response)

        # Extract list of roles (by splitting commas or lines)
        roles = [r.strip() for r in re.split(r",|\n", response) if r.strip()]

        # Remove any extra commentary
        garbage_phrases = [
            "Based on", "the candidate", "skills", "match", "are", "here", "most relevant", "suggested roles"
        ]
        roles = [r for r in roles if not any(p in r.lower() for p in garbage_phrases)]

        return {"roles": roles[:3]}  # Limit to top 3
    except Exception as e:
        print("Role extraction error:", e)
        return {"roles": []}

# ------------------ Fetch Job Descriptions ------------------
def fetch_dynamic_jds(role):
    prompt = f"""
Generate 2 short job descriptions for the role '{role}'.

Each job description should be in one sentence and clearly mention technical and soft skills in a comma-separated list.

Format:
[
  "We are hiring a Machine Learning Engineer with experience in Python, TensorFlow, Docker, AWS, communication, problem-solving.",
  "The role requires skills in Scikit-learn, Kubernetes, cloud platforms like Azure, teamwork, and analytical thinking."
]
Return this as a valid JSON list.
"""
    try:
        raw = query_groq(prompt)
        print(" Raw JD response:", raw)
        return json.loads(raw)
    except Exception as e:
        print(" JD fetch error:", e)
        # Fallback: split lines
        return [line for line in raw.split('\n') if line.strip()]




# ------------------ Roadmap PDF ------------------
def generate_roadmap_pdf(skills):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.set_title("SkillSnap AI - Learning Roadmap")

    pdf.cell(200, 10, txt="SkillSnap AI - Learning Roadmap", ln=True, align='C')
    pdf.ln(10)

    # Filter junk
    garbage_phrases = [
        "Here are the skills", "Note that", "I did not include",
        "Here is the list", "format you requested", "extracted from the text"
    ]

    cleaned_skills = []
    for skill in skills:
        if any(g.lower() in skill.lower() for g in garbage_phrases):
            continue
        cleaned = re.sub(r"[^\w\s.+\-]", "", skill).strip().rstrip(".")
        if cleaned and cleaned.lower() not in [s.lower() for s in cleaned_skills]:
            cleaned_skills.append(cleaned)

    for skill in cleaned_skills:
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, f"{skill}")
        pdf.set_font("Arial", size=10)
        pdf.multi_cell(0, 8, f"    Coursera: https://www.coursera.org/search?query={skill.replace(' ', '%20')}")
        pdf.multi_cell(0, 8, f"    Udemy: https://www.udemy.com/courses/search/?q={skill.replace(' ', '%20')}")
        pdf.multi_cell(0, 8, f"    YouTube: https://www.youtube.com/results?search_query=learn+{skill.replace(' ', '+')}")
        pdf.ln(4)

    pdf.output("roadmap.pdf")
    return "roadmap.pdf"



# ------------------ Skill Gap Analysis ------------------
def analyze_skill_gap(resume_text, role):
    resume_skills = set(extract_skills(resume_text))
    print(" Extracted Resume Skills:", resume_skills)

    job_descriptions = fetch_dynamic_jds(role)
    if not job_descriptions:
        print(" No job descriptions returned.")
        return {
            "resume_skills": list(resume_skills),
            "job_required_skills": [],
            "missing_skills": []
        }

    print(" Job Descriptions Returned:", job_descriptions)

    all_job_skills = set()
    for i, jd in enumerate(job_descriptions):
        jd_skills = set(extract_skills(jd))
        print(f" Skills from JD {i+1}:", jd_skills)
        all_job_skills.update(jd_skills)

    missing = list(all_job_skills - resume_skills)

    return {
        "resume_skills": list(resume_skills),
        "job_required_skills": list(all_job_skills),
        "missing_skills": missing
    }



# ------------------ Routes ------------------
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_resume():
    global stored_resume_text
    resume = request.files.get('resume')
    if not resume:
        return jsonify({"error": "No file uploaded"}), 400

    stored_resume_text = extract_text_from_resume(resume)
    return jsonify({"message": "Resume uploaded successfully"})

@app.route('/ats-score', methods=['GET'])
def ats_score():
    global stored_resume_text
    if not stored_resume_text:
        return jsonify({"error": "No resume uploaded"}), 400

    ats = get_ats_score(stored_resume_text)
    roles = recommend_roles(stored_resume_text)

    return jsonify({
        "ats": ats,
        "recommended_roles": roles.get("roles", [])
    })

@app.route('/skill-gap', methods=['POST'])
def skill_gap():
    global stored_resume_text
    if not stored_resume_text:
        return jsonify({"error": "No resume uploaded"}), 400

    role = request.form.get('role')
    if not role:
        return jsonify({"error": "Job role is required"}), 400

    gap_data = analyze_skill_gap(stored_resume_text, role)
    generate_roadmap_pdf(gap_data["missing_skills"])

    return jsonify({
        "resume_skills": gap_data["resume_skills"],
        "required_skills": gap_data["job_required_skills"],
        "missing_skills": gap_data["missing_skills"],
        "roadmap_pdf": f"/{ROADMAP_FILE}"
    })

@app.route('/roadmap.pdf')
def download_pdf():
    return send_from_directory('.', ROADMAP_FILE, as_attachment=True)

# ------------------ Main ------------------
if __name__ == '__main__':
    app.run(debug=True)
