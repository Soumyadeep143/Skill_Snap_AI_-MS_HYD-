# 🚀 SkillSnap AI – Resume Analyzer (MS HYD Project)

**SkillSnap AI** is an intelligent resume analysis tool built using Python (Flask) and powered by **Groq's LLaMA 3 API**.  
It evaluates resumes based on ATS standards, suggests job roles, detects skill gaps, and generates a **PDF roadmap** with curated learning links from **Coursera**, **Udemy**, and **YouTube**.

---
## 📛 Project Badges

![Python Version](https://img.shields.io/badge/python-3.11-blue?logo=python)
![Poetry](https://img.shields.io/badge/poetry-dependency--manager-brightgreen?logo=python)


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

```
## 🦾 Install Dependencies

You can install the required libraries using either **pip** or **Poetry**, depending on your setup.

### Using pip
```bash
pip install -r requirements.txt
```
### Using poetry
```bash
poetry install
```


 

