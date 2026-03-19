from __future__ import annotations

from typing import Sequence


def normalize_skill_names(predictions: Sequence[dict[str, object] | str]) -> list[str]:
    seen: set[str] = set()
    skill_names: list[str] = []

    for prediction in predictions:
        if isinstance(prediction, dict):
            name = str(prediction.get("name", "")).strip()
        else:
            name = str(prediction).strip()

        if not name or name in seen:
            continue

        seen.add(name)
        skill_names.append(name)

    return skill_names


def build_resume_match(job_predictions: Sequence[dict[str, object]], resume_predictions: Sequence[dict[str, object]]) -> dict[str, object]:
    job_skills = normalize_skill_names(job_predictions)
    resume_skills = normalize_skill_names(resume_predictions)
    resume_skill_set = set(resume_skills)
    job_skill_set = set(job_skills)

    matched_skills = [skill for skill in job_skills if skill in resume_skill_set]
    missing_skills = [skill for skill in job_skills if skill not in resume_skill_set]
    resume_only_skills = [skill for skill in resume_skills if skill not in job_skill_set]

    match_percentage = round(len(matched_skills) / len(job_skills), 4) if job_skills else 0.0

    return {
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "resume_only_skills": resume_only_skills,
        "match_percentage": match_percentage,
        "matched_skill_count": len(matched_skills),
        "missing_skill_count": len(missing_skills),
        "job_skill_count": len(job_skills),
        "resume_skill_count": len(resume_skills),
    }
