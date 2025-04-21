import streamlit as st
import requests
import fitz  # PyMuPDF

# === Hugging Face Setup ===
NLI_MODEL = "facebook/bart-large-mnli"

HEADERS = {"Authorization": "Bearer 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"}  # Replace with your token

# === Skill Sets by Role ===
essential_skills = {
    "Data Scientist": ["Python", "Pandas", "Machine Learning", "SQL", "Statistics", "Deep Learning", "Data Visualization"],
    "Software Engineer": ["JavaScript", "React", "Node.js", "Databases", "Git", "APIs", "Algorithms"],
    "Product Manager": ["Roadmap", "User Research", "Agile", "KPIs", "Wireframes", "Leadership"],
}

job_labels = list(essential_skills.keys())

# === Functions ===
def extract_text_from_pdf(uploaded_file):
    text = ""
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    for page in doc:
        text += page.get_text()
    return text

def classify_resume(text):
    payload = {
        "inputs": text,
        "parameters": {
            "candidate_labels": job_labels,
            "multi_label": True
        }
    }
    response = requests.post(f"https://api-inference.huggingface.co/models/{NLI_MODEL}", headers=HEADERS, json=payload)
    return response.json()

import re

def detect_skill_gaps(resume_text, selected_role):
    # Convert the resume text to lower case for case-insensitive comparison
    resume_text_lower = resume_text.lower()

    # List of essential skills for the selected role
    required_skills = essential_skills[selected_role]

    found_skills = []
    missing_skills = []

    # Check each skill for its occurrence in the resume text (case-insensitive, whole word matching)
    for skill in required_skills:
        # Use regular expression to match whole words only (avoid partial matches)
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'

        if re.search(pattern, resume_text_lower):
            found_skills.append(skill)
        else:
            missing_skills.append(skill)

    return found_skills, missing_skills


# === Streamlit UI ===
st.set_page_config(page_title="📄 AI Resume Analyzer", layout="centered")
st.title("📄 AI Resume Analyzer + Skill Gap Detector")

upload_option = st.radio("Choose input method", ["Upload File", "Paste Text"])
resume_text = ""

if upload_option == "Upload File":
    uploaded_file = st.file_uploader("Upload your resume (.pdf or .txt)", type=["pdf", "txt"])
    if uploaded_file:
        if uploaded_file.name.endswith(".pdf"):
            resume_text = extract_text_from_pdf(uploaded_file)
        elif uploaded_file.name.endswith(".txt"):
            resume_text = uploaded_file.read().decode("utf-8")
elif upload_option == "Paste Text":
    resume_text = st.text_area("Paste your resume text here")

if resume_text.strip() and st.button("Analyze Resume"):
    with st.spinner("Analyzing your resume..."):
        result = classify_resume(resume_text)
   

        st.subheader("🔍 Job Role Match Scores:")
        for label, score in zip(result["labels"], result["scores"]):
            st.write(f"**{label}** — {score * 100:.2f}% match")

   

        st.subheader("📊 Skill Gap Detection:")
        selected_role = st.selectbox("Select a job role for skill gap analysis", job_labels)
        found, missing = detect_skill_gaps(resume_text, selected_role)

        st.write(f"✅ **Skills Found for {selected_role}:** {', '.join(found) if found else 'None'}")
        st.write(f"❌ **Missing Key Skills:** {', '.join(missing) if missing else 'None – Great Match!'}")


