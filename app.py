from flask import Flask, render_template, request
from pypdf import PdfReader
import re

app = Flask(__name__)

app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB maximum PDF size


SKILLS = [
    "java",
    "python",
    "javascript",
    "typescript",
    "sql",
    "html",
    "css",
    "react",
    "flask",
    "spring boot",
    "spring framework",
    "spring mvc",
    "hibernate",
    "rest api",
    "rest apis",
    "microservices",
    "docker",
    "aws",
    "postgresql",
    "mysql",
    "mongodb",
    "redis",
    "kafka",
    "kubernetes",
    "junit",
    "git",
    "github",
    "openai",
    "langchain",
    "machine learning",
    "artificial intelligence",
    "cloud computing",
    "data structures",
    "algorithms",
]


def extract_resume_text(pdf_file):
    """Extract text from an uploaded PDF resume."""
    reader = PdfReader(pdf_file.stream)

    pages_text = []

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            pages_text.append(page_text)

    return "\n".join(pages_text)


def find_skills(text):
    """Find known technical skills in text."""
    text = text.lower()
    found_skills = set()

    for skill in SKILLS:
        pattern = rf"(?<!\w){re.escape(skill)}(?!\w)"

        if re.search(pattern, text):
            found_skills.add(skill)

    return found_skills


def calculate_match(resume_text, job_description):
    """Compare resume skills with job-description skills."""
    resume_skills = find_skills(resume_text)
    job_skills = find_skills(job_description)

    matched_skills = sorted(resume_skills.intersection(job_skills))
    missing_skills = sorted(job_skills.difference(resume_skills))

    if len(job_skills) > 0:
        score = round((len(matched_skills) / len(job_skills)) * 100)
    else:
        score = 0

    return score, matched_skills, missing_skills


@app.route("/", methods=["GET", "POST"])
@app.route("/analyze", methods=["POST"])
def home():
    if request.method == "GET":
        return render_template("index.html")

    resume_file = request.files.get("resume")
    job_description = request.form.get("job_description", "").strip()

    if resume_file is None or resume_file.filename == "":
        return render_template(
            "index.html",
            error="Please upload your resume PDF."
        )

    if not resume_file.filename.lower().endswith(".pdf"):
        return render_template(
            "index.html",
            error="Please upload a PDF file only."
        )

    if not job_description:
        return render_template(
            "index.html",
            error="Please enter a job description."
        )

    try:
        resume_text = extract_resume_text(resume_file)
    except Exception as error:
        return render_template(
            "index.html",
            error=f"Could not read the PDF file: {error}"
        )

    if not resume_text.strip():
        return render_template(
            "index.html",
            error="No readable text was found in the PDF."
        )

    score, matched_skills, missing_skills = calculate_match(
        resume_text,
        job_description
    )

    return render_template(
        "result.html",
        score=score,
        match_score=score,
        score_percent=f"{score}%",
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        matched_keywords=matched_skills,
        missing_keywords=missing_skills,
        resume_text=resume_text,
        job_description=job_description,
    )


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)