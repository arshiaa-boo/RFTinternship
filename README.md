# 🧠 AI Resume Screening Tool — Day 26

An end-to-end Python project that reads resumes, extracts candidate
details, matches them against a job description, scores/ranks
candidates, highlights missing skills, and exports a shortlist to CSV.
Includes a bonus Streamlit web UI.

## 📁 Project Structure

```
resume_screener/
├── resume_parser.py         # Extracts Name, Email, Skills, Experience, Education
├── scorer.py                 # TF-IDF similarity + skill-coverage scoring engine
├── main.py                   # CLI pipeline: load -> score -> rank -> export CSV
├── streamlit_app.py          # Bonus: web UI for uploading & screening resumes
├── job_description.txt       # Sample job description
├── sample_resumes/           # 4 sample .txt resumes to test with
│   ├── resume_1.txt
│   ├── resume_2.txt
│   ├── resume_3.txt
│   └── resume_4.txt
├── requirements.txt
└── README.md
```

## 🚀 Setup

```bash
pip install -r requirements.txt
```

## ▶️ Run the CLI version

```bash
python main.py \
  --resumes_folder sample_resumes \
  --job_description job_description.txt \
  --required_skills "python,sql,pandas,scikit-learn,aws,machine learning" \
  --min_experience 2 \
  --shortlist_threshold 50 \
  --output shortlisted_candidates.csv
```

This prints a ranked leaderboard to the console and writes
`shortlisted_candidates.csv` with every candidate whose match score
meets the threshold.

You can also read resumes from a CSV instead of a folder of `.txt`
files — pass `--resumes_csv resumes.csv` (the CSV needs a
`resume_text` column holding each candidate's full resume text).

## 🌐 Run the Streamlit app (bonus)

```bash
streamlit run streamlit_app.py
```

Then in the browser:
1. Paste a job description in the sidebar.
2. Set required skills and adjust scoring weights if you like.
3. Upload one or more `.txt` resumes (try the files in `sample_resumes/`).
4. Click **Screen Resumes** to see the ranked table, per-candidate
   detail cards with missing-skill warnings, and download the
   shortlist as CSV.

## 🧮 How scoring works

Each resume gets a **Match Score (0–100)** made of three parts:

| Component | Weight (default) | What it measures |
|---|---|---|
| Text similarity | 50% | TF-IDF cosine similarity between the full resume text and the job description |
| Skill coverage | 40% | % of the job's required skills found in the resume |
| Experience fit | 10% | Candidate's years of experience vs. the minimum you set |

Weights are configurable — in the CLI by editing the `weights` dict
passed to `score_candidates()` in `main.py`, or live in the Streamlit
sidebar sliders.

## ✏️ Customizing skill/education detection

`resume_parser.py` uses two editable lists:
- `SKILL_DB` — the full vocabulary of skills the tool looks for.
- `EDUCATION_KEYWORDS` — degree keywords used to detect education level.

Add or remove entries to match the roles you're screening for (e.g.
add "photoshop", "figma", "salesforce" for design/sales roles).

## 📝 Notes on the approach

This is a deliberately transparent, rule-based pipeline (regex +
keyword matching + TF-IDF), not a deep-learning model — which makes it:
- Fast and free to run (no API keys or GPU needed).
- Explainable: you can see exactly *why* a candidate scored the way
  they did (which skills matched/were missing, similarity %, etc.).
- Easy to extend: swap in spaCy NER for name/entity extraction, or a
  sentence-embedding model (e.g. `sentence-transformers`) instead of
  TF-IDF, for stronger semantic matching if you outgrow this version.

## 💡 Sample resumes included

`sample_resumes/` has 4 test resumes with varying skill overlap
against `job_description.txt` (a Python/Data Scientist role) so you
can see strong, moderate, and weak matches right away.
