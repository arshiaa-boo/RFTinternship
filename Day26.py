
import argparse
import pandas as pd

from resume_parser import load_resumes_from_folder, load_resumes_from_csv
from scorer import score_candidates


def run(resumes_folder=None, resumes_csv=None, job_description_path=None,
         required_skills=None, min_experience=0, top_n=10,
         shortlist_threshold=50, output="shortlisted_candidates.csv"):

    # 1. Load resumes
    if resumes_csv:
        resumes = load_resumes_from_csv(resumes_csv)
    else:
        resumes = load_resumes_from_folder(resumes_folder)

    if not resumes:
        print("No resumes found. Check your --resumes_folder / --resumes_csv path.")
        return

    # 2. Load job description
    with open(job_description_path, "r", encoding="utf-8") as f:
        job_description = f.read()

    # 3. Score & rank
    results = score_candidates(
        resumes=resumes,
        job_description=job_description,
        required_skills=required_skills,
        min_experience_years=min_experience,
    )

    df = pd.DataFrame(results)
    df = df[[
        "rank", "name", "email", "phone", "match_score", "text_similarity_pct",
        "skill_coverage_pct", "experience_years", "education",
        "matched_skills", "missing_skills", "source_file",
    ]]

    # 4. Print a quick leaderboard to the console
    print("\n=== Resume Match Leaderboard ===")
    print(df.head(top_n).to_string(index=False))

    # 5. Shortlist candidates above the threshold and export
    shortlisted = df[df["match_score"] >= shortlist_threshold]
    shortlisted.to_csv(output, index=False)
    print(f"\n{len(shortlisted)} candidate(s) scored >= {shortlist_threshold} "
          f"and were exported to '{output}'")

    return df


def _parse_args():
    p = argparse.ArgumentParser(description="AI Resume Screening Tool")
    p.add_argument("--resumes_folder", default="sample_resumes",
                    help="Folder containing .txt resumes")
    p.add_argument("--resumes_csv", default=None,
                    help="Optional CSV file of resumes instead of a folder "
                         "(expects a 'resume_text' column)")
    p.add_argument("--job_description", default="job_description.txt",
                    help="Path to a .txt file with the job description")
    p.add_argument("--required_skills",
                    default="python,sql,machine learning,pandas,aws",
                    help="Comma-separated list of required skills")
    p.add_argument("--min_experience", type=float, default=2,
                    help="Years of experience considered fully qualified")
    p.add_argument("--top_n", type=int, default=10,
                    help="How many top candidates to print to console")
    p.add_argument("--shortlist_threshold", type=float, default=50,
                    help="Minimum match_score (0-100) to be shortlisted")
    p.add_argument("--output", default="shortlisted_candidates.csv",
                    help="Output CSV filename")
    return p.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    run(
        resumes_folder=args.resumes_folder,
        resumes_csv=args.resumes_csv,
        job_description_path=args.job_description,
        required_skills=[s.strip() for s in args.required_skills.split(",")],
        min_experience=args.min_experience,
        top_n=args.top_n,
        shortlist_threshold=args.shortlist_threshold,
        output=args.output,
    )


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


from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from resume_parser import _extract_skills, EXPERIENCE_RE


def _text_similarity_scores(resume_texts: list, job_description: str) -> list:
    """Return a 0-100 TF-IDF cosine similarity score for each resume."""
    corpus = [job_description] + resume_texts
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(corpus)
    job_vector = tfidf_matrix[0:1]
    resume_vectors = tfidf_matrix[1:]
    sims = cosine_similarity(job_vector, resume_vectors)[0]
    return [round(s * 100, 2) for s in sims]


def _skill_match(candidate_skills: list, required_skills: list) -> dict:
    candidate_set = set(candidate_skills)
    required_set = set(s.lower().strip() for s in required_skills)
    matched = sorted(candidate_set & required_set)
    missing = sorted(required_set - candidate_set)
    coverage = (len(matched) / len(required_set) * 100) if required_set else 0
    return {
        "matched_skills": matched,
        "missing_skills": missing,
        "skill_coverage_pct": round(coverage, 2),
    }


def score_candidates(resumes: list, job_description: str, required_skills: list,
                      min_experience_years: float = 0,
                      weights: dict = None) -> list:
    """
    resumes: list of parsed resume dicts (from resume_parser.parse_resume_text)
    job_description: raw text of the job description
    required_skills: list of skill strings the role needs
    min_experience_years: years of experience considered "fully qualified"
    weights: {"similarity": .., "skills": .., "experience": ..} summing to 1.0
    """
    if weights is None:
        weights = {"similarity": 0.5, "skills": 0.4, "experience": 0.1}

    resume_texts = [r["raw_text"] for r in resumes]
    similarity_scores = _text_similarity_scores(resume_texts, job_description)

    results = []
    for resume, sim_score in zip(resumes, similarity_scores):
        skill_info = _skill_match(resume["skills"], required_skills)

        exp_years = resume["experience_years"]
        exp_score = 100 if min_experience_years == 0 else min(
            100, round((exp_years / min_experience_years) * 100, 2)
        )

        final_score = round(
            sim_score * weights["similarity"]
            + skill_info["skill_coverage_pct"] * weights["skills"]
            + exp_score * weights["experience"],
            2,
        )

        results.append({
            "name": resume["name"],
            "email": resume["email"],
            "phone": resume["phone"],
            "source_file": resume["source_file"],
            "experience_years": exp_years,
            "education": resume["education"],
            "matched_skills": ", ".join(skill_info["matched_skills"]),
            "missing_skills": ", ".join(skill_info["missing_skills"]),
            "skill_coverage_pct": skill_info["skill_coverage_pct"],
            "text_similarity_pct": sim_score,
            "match_score": final_score,
        })

    results.sort(key=lambda r: r["match_score"], reverse=True)
    for i, r in enumerate(results, start=1):
        r["rank"] = i
    return results


import streamlit as st
import pandas as pd

from resume_parser import parse_resume_text
from scorer import score_candidates

st.set_page_config(page_title="AI Resume Screening Tool", layout="wide")

st.title("🧠 AI Resume Screening Tool")
st.caption("Upload resumes, paste a job description, and get a ranked, "
           "explainable match score for every candidate.")

# ---------------------------------------------------------------------
# Sidebar: job description & scoring settings
# ---------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Job Setup")
    job_description = st.text_area(
        "Job Description", height=220,
        placeholder="Paste the job description here...",
    )
    required_skills_raw = st.text_input(
        "Required Skills (comma-separated)",
        value="python, sql, pandas, scikit-learn, aws, machine learning",
    )
    min_experience = st.number_input(
        "Minimum experience considered 'fully qualified' (years)",
        min_value=0.0, value=2.0, step=0.5,
    )
    shortlist_threshold = st.slider(
        "Shortlist threshold (match score)", 0, 100, 50,
    )
    st.markdown("---")
    w_sim = st.slider("Weight: Text Similarity", 0.0, 1.0, 0.5, 0.05)
    w_skill = st.slider("Weight: Skill Coverage", 0.0, 1.0, 0.4, 0.05)
    w_exp = st.slider("Weight: Experience Fit", 0.0, 1.0, 0.1, 0.05)

# ---------------------------------------------------------------------
# Main: resume upload
# ---------------------------------------------------------------------
uploaded_files = st.file_uploader(
    "Upload resumes (.txt files, multiple allowed)",
    type=["txt"], accept_multiple_files=True,
)

run_button = st.button("🔍 Screen Resumes", type="primary")

if run_button:
    if not uploaded_files:
        st.warning("Please upload at least one resume (.txt).")
    elif not job_description.strip():
        st.warning("Please paste a job description in the sidebar.")
    else:
        resumes = []
        for f in uploaded_files:
            text = f.read().decode("utf-8", errors="ignore")
            resumes.append(parse_resume_text(text, source_file=f.name))

        required_skills = [s.strip() for s in required_skills_raw.split(",") if s.strip()]

        total_w = w_sim + w_skill + w_exp
        weights = {
            "similarity": w_sim / total_w if total_w else 0.5,
            "skills": w_skill / total_w if total_w else 0.4,
            "experience": w_exp / total_w if total_w else 0.1,
        }

        results = score_candidates(
            resumes=resumes,
            job_description=job_description,
            required_skills=required_skills,
            min_experience_years=min_experience,
            weights=weights,
        )
        df = pd.DataFrame(results)

        st.success(f"Screened {len(df)} resume(s).")

        # --- Leaderboard ---
        st.subheader("🏆 Ranked Candidates")
        display_df = df[[
            "rank", "name", "match_score", "text_similarity_pct",
            "skill_coverage_pct", "experience_years", "education",
            "matched_skills", "missing_skills", "source_file",
        ]]
        st.dataframe(
            display_df.style.background_gradient(subset=["match_score"], cmap="Greens"),
            use_container_width=True,
        )

        # --- Per-candidate detail cards ---
        st.subheader("📋 Candidate Details")
        for _, row in df.iterrows():
            with st.expander(f"#{row['rank']} — {row['name']} ({row['match_score']}%)"):
                c1, c2, c3 = st.columns(3)
                c1.metric("Match Score", f"{row['match_score']}%")
                c2.metric("Skill Coverage", f"{row['skill_coverage_pct']}%")
                c3.metric("Experience", f"{row['experience_years']} yrs")
                st.write(f"**Email:** {row['email']}  |  **Phone:** {row['phone']}")
                st.write(f"**Education:** {row['education']}")
                st.write(f"✅ **Matched skills:** {row['matched_skills'] or '—'}")
                if row["missing_skills"]:
                    st.warning(f"⚠️ **Missing skills:** {row['missing_skills']}")
                else:
                    st.info("No required skills missing.")

        # --- Shortlist + export ---
        shortlisted = df[df["match_score"] >= shortlist_threshold]
        st.subheader(f"✅ Shortlisted Candidates (score ≥ {shortlist_threshold})")
        st.dataframe(shortlisted[display_df.columns], use_container_width=True)

        csv_bytes = shortlisted[display_df.columns].to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download Shortlisted Candidates (CSV)",
            data=csv_bytes,
            file_name="shortlisted_candidates.csv",
            mime="text/csv",
        )
else:
    st.info("Upload resumes and click **Screen Resumes** to get started. "
            "Sample .txt resumes are included in the `sample_resumes/` folder "
            "if you want to try it immediately.")
