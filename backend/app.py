#!/usr/bin/env python3
"""
FastAPI backend for candidate skill extraction.
"""

from __future__ import annotations

from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from skill_extractor import build_output, extract_skills, load_lexicon


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_LEXICON_PATH = BASE_DIR / "skills_lexicon.json"
SAMPLE_JOB_DESCRIPTION_PATH = BASE_DIR / "sample_job_description.txt"


class ExtractRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Job description text to parse.")
    min_confidence: float = Field(default=0.30, ge=0.0, le=1.0)
    top_evidence: int = Field(default=2, ge=1, le=10)
    lexicon_path: str | None = Field(default=None, description="Optional path to a custom lexicon file.")


app = FastAPI(title="Candidate Skill Extraction API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def resolve_lexicon_path(path: str | None) -> str:
    if not path:
        return str(DEFAULT_LEXICON_PATH)

    candidate = Path(path)
    if candidate.is_absolute():
        return str(candidate)

    return str(BASE_DIR / candidate)


@app.get("/api/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/sample")
def get_sample_job_description() -> dict[str, str]:
    return {"text": SAMPLE_JOB_DESCRIPTION_PATH.read_text(encoding="utf-8")}


@app.post("/api/extract")
def extract_job_skills(payload: ExtractRequest) -> dict[str, object]:
    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Job description text is empty.")

    try:
        lexicon = load_lexicon(resolve_lexicon_path(payload.lexicon_path))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to load lexicon: {exc}") from exc

    matches = extract_skills(
        text=text,
        lexicon=lexicon,
        min_confidence=payload.min_confidence,
        top_evidence=payload.top_evidence,
    )
    return build_output(matches)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
