

import re
import os
import csv

# ----------------------------------------------------------------------
# Reference data — extend these lists to fit your domain / role.
# ----------------------------------------------------------------------
SKILL_DB = [
    "python", "java", "c++", "c#", "javascript", "typescript", "sql", "r",
    "html", "css", "react", "angular", "vue", "node.js", "django", "flask",
    "fastapi", "streamlit", "pandas", "numpy", "scikit-learn", "tensorflow",
    "pytorch", "keras", "machine learning", "deep learning", "nlp",
    "computer vision", "data analysis", "data visualization", "power bi",
    "tableau", "excel", "aws", "azure", "gcp", "docker", "kubernetes",
    "git", "github", "ci/cd", "linux", "rest api", "graphql", "mongodb",
    "mysql", "postgresql", "spark", "hadoop", "airflow", "agile", "scrum",
]

EDUCATION_KEYWORDS = [
    "phd", "ph.d", "doctorate", "master", "m.tech", "m.sc", "msc", "mba",
    "bachelor", "b.tech", "b.sc", "bsc", "be ", "b.e.", "diploma",
    "associate degree", "high school",
]

EMAIL_RE = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
PHONE_RE = re.compile(r"(\+?\d[\d\-\s()]{8,}\d)")
# Matches things like "5 years", "5+ years", "3-5 years of experience"
EXPERIENCE_RE = re.compile(
    r"(\d+)\s*\+?\s*-?\s*(?:to\s*\d+\s*)?\s*years?\b", re.IGNORECASE
)


def _guess_name(text: str) -> str:
    """Assume the candidate's name is on the first non-empty line,
    unless that line looks like a header such as 'Resume' or 'CV'."""
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if re.match(r"^(resume|curriculum vitae|cv)\b", line, re.IGNORECASE):
            continue
        # A name line is usually short and has no digits / @ symbol
        if len(line.split()) <= 5 and "@" not in line and not any(c.isdigit() for c in line):
            return line
        break
    return "Unknown"


def _extract_skills(text: str) -> list:
    text_lower = text.lower()
    found = []
    for skill in SKILL_DB:
        # word-boundary-ish match so "r" doesn't match inside "career"
        pattern = r"(?<![a-zA-Z0-9])" + re.escape(skill) + r"(?![a-zA-Z0-9])"
        if re.search(pattern, text_lower):
            found.append(skill)
    return sorted(set(found))


def _extract_experience_years(text: str) -> float:
    matches = EXPERIENCE_RE.findall(text)
    years = [int(m) for m in matches if m.isdigit()]
    return max(years) if years else 0


def _extract_education(text: str) -> str:
    text_lower = text.lower()
    found = []
    for kw in EDUCATION_KEYWORDS:
        if kw in text_lower:
            found.append(kw.replace(".", "").strip().title())
    # de-duplicate while preserving order, keep the highest-sounding ones
    seen = []
    for f in found:
        if f not in seen:
            seen.append(f)
    return ", ".join(seen) if seen else "Not specified"


def parse_resume_text(text: str, source_file: str = "") -> dict:
    """Parse a single resume's raw text into a structured dict."""
    email_match = EMAIL_RE.search(text)
    phone_match = PHONE_RE.search(text)
    return {
        "source_file": source_file,
        "name": _guess_name(text),
        "email": email_match.group(0) if email_match else "Not found",
        "phone": phone_match.group(0).strip() if phone_match else "Not found",
        "skills": _extract_skills(text),
        "experience_years": _extract_experience_years(text),
        "education": _extract_education(text),
        "raw_text": text,
    }


def load_resumes_from_folder(folder_path: str) -> list:
    """Read every .txt resume in a folder and parse it."""
    resumes = []
    for fname in sorted(os.listdir(folder_path)):
        if fname.lower().endswith(".txt"):
            fpath = os.path.join(folder_path, fname)
            with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
            resumes.append(parse_resume_text(text, source_file=fname))
    return resumes


def load_resumes_from_csv(csv_path: str, text_column: str = "resume_text",
                           name_column: str = None) -> list:
    """Read resumes from a CSV where one column holds the full resume text.

    Useful when resumes have been bulk-exported into a spreadsheet instead
    of individual .txt files.
    """
    resumes = []
    with open(csv_path, "r", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            text = row.get(text_column, "")
            parsed = parse_resume_text(text, source_file=f"csv_row_{i+1}")
            if name_column and row.get(name_column):
                parsed["name"] = row[name_column]
            resumes.append(parsed)
    return resumes
