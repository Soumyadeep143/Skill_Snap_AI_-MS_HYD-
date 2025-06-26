# 🚀 SkillSnap AI – Resume Analyzer (MS HYD Project)

**SkillSnap AI** is an intelligent resume analysis tool built using Python (Flask) and powered by **Groq's LLaMA 3 API**.  
It evaluates resumes based on ATS standards, suggests job roles, detects skill gaps, and generates a **PDF roadmap** with curated learning links from **Coursera**, **Udemy**, and **YouTube**.

---

## 📌 Features

✅ Upload resume (`.pdf` or `.docx`)  
✅ Get ATS Score out of 100  
✅ Receive top 3 suggested tech job roles  
✅ Analyze skill gap for any job role  
✅ Download personalized learning roadmap PDF  
✅ Groq LLM (LLaMA 3) API-powered NLP  

---

## 📁 Project Structure

```bash
.
├── app.py                  # Main Flask application
├── templates/
│   └── index.html          # Frontend UI
├── static/                 # (Optional for CSS/JS)
├── roadmap.pdf             # Generated dynamically
├── requirements.txt        # Python dependencies
└── README.md               # You're reading this file
