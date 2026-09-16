

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
