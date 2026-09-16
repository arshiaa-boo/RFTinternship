

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
