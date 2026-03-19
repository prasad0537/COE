from __future__ import annotations

import os
import sys
from functools import lru_cache
from pathlib import Path

import joblib
import numpy as np
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field


PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
FRONTEND_BUILD_DIR = PROJECT_ROOT / "frontend" / "build"
FRONTEND_STATIC_DIR = FRONTEND_BUILD_DIR / "static"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from common import DEFAULT_MODEL_PATH, DEFAULT_SAMPLE_TEXT_PATH  # noqa: E402
from resume_matcher import build_resume_match  # noqa: E402


class PredictRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Job description text.")
    threshold: float | None = Field(default=None, ge=0.0, le=1.0)
    top_k: int = Field(default=12, ge=1, le=50)
    min_predictions: int = Field(default=5, ge=1, le=50)


class ResumeMatchRequest(BaseModel):
    job_text: str = Field(..., min_length=1, description="Job description text.")
    resume_text: str = Field(..., min_length=1, description="Candidate resume text.")
    threshold: float | None = Field(default=None, ge=0.0, le=1.0)
    top_k: int = Field(default=12, ge=1, le=50)
    min_predictions: int = Field(default=5, ge=1, le=50)


app = FastAPI(title="Skill Prediction API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if FRONTEND_STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=FRONTEND_STATIC_DIR), name="static")


@lru_cache(maxsize=1)
def load_bundle() -> dict[str, object]:
    if not DEFAULT_MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model file not found at {DEFAULT_MODEL_PATH}. Run 'python src\\train_model.py' first."
        )
    return joblib.load(DEFAULT_MODEL_PATH)


def ensure_non_empty_prediction(probabilities: np.ndarray, selected_indexes: list[int]) -> list[int]:
    if selected_indexes:
        return selected_indexes
    return [int(np.argmax(probabilities))]


def pad_predictions(order: np.ndarray, selected_indexes: list[int], min_predictions: int, top_k: int) -> list[int]:
    padded = list(selected_indexes)
    for index in order:
        value = int(index)
        if value in padded:
            continue
        if len(padded) >= min(min_predictions, top_k):
            break
        padded.append(value)
    return padded[:top_k]


def predict_skills(text: str, threshold: float | None, top_k: int, min_predictions: int) -> dict[str, object]:
    bundle = load_bundle()
    vectorizer = bundle["vectorizer"]
    classifier = bundle["model"]
    label_binarizer = bundle["label_binarizer"]
    model_threshold = float(threshold) if threshold is not None else float(bundle["threshold"])
    lexicon_by_name = {entry["name"]: entry for entry in bundle["lexicon"]}

    probabilities = classifier.predict_proba(vectorizer.transform([text]))[0]
    order = np.argsort(probabilities)[::-1]
    selected = [int(index) for index in order if probabilities[index] >= model_threshold][:top_k]
    selected = ensure_non_empty_prediction(probabilities, selected)
    selected = pad_predictions(order, selected, min_predictions, top_k)

    predictions = []
    categories: dict[str, int] = {}
    for index in selected:
        name = str(label_binarizer.classes_[index])
        category = str(lexicon_by_name.get(name, {}).get("category", "Uncategorized"))
        confidence = round(float(probabilities[index]), 4)
        predictions.append(
            {
                "name": name,
                "category": category,
                "confidence": confidence,
            }
        )
        categories[category] = categories.get(category, 0) + 1

    return {
        "summary": {
            "total_predicted_skills": len(predictions),
            "threshold": float(model_threshold),
            "top_category": max(categories, key=categories.get) if categories else None,
        },
        "predicted_skills": predictions,
    }


def match_resume_to_job(
    job_text: str,
    resume_text: str,
    threshold: float | None,
    top_k: int,
    min_predictions: int,
) -> dict[str, object]:
    job_prediction = predict_skills(
        text=job_text,
        threshold=threshold,
        top_k=top_k,
        min_predictions=min_predictions,
    )
    resume_prediction = predict_skills(
        text=resume_text,
        threshold=threshold,
        top_k=top_k,
        min_predictions=min_predictions,
    )
    match = build_resume_match(
        job_predictions=job_prediction["predicted_skills"],
        resume_predictions=resume_prediction["predicted_skills"],
    )

    return {
        **job_prediction,
        "resume_prediction": resume_prediction,
        "match": match,
    }


def frontend_available() -> bool:
    return (FRONTEND_BUILD_DIR / "index.html").exists()


def frontend_response(path: str = "index.html") -> Response:
    if not frontend_available():
        return JSONResponse(
            status_code=503,
            content={
                "detail": "Frontend build not found. Run 'npm run build' inside the frontend directory."
            },
        )

    candidate = (FRONTEND_BUILD_DIR / path).resolve()
    if candidate.is_file() and FRONTEND_BUILD_DIR in candidate.parents:
        return FileResponse(candidate)

    return FileResponse(FRONTEND_BUILD_DIR / "index.html")


@app.get("/", include_in_schema=False)
def root() -> Response:
    if frontend_available():
        return frontend_response()
    return RedirectResponse(url="/docs")


@app.get("/api/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/sample")
def get_sample_text() -> dict[str, str]:
    return {"text": DEFAULT_SAMPLE_TEXT_PATH.read_text(encoding="utf-8")}


@app.post("/api/predict")
def predict(payload: PredictRequest) -> dict[str, object]:
    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Input text is empty.")

    try:
        return predict_skills(
            text=text,
            threshold=payload.threshold,
            top_k=payload.top_k,
            min_predictions=payload.min_predictions,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/match")
def match_resume(payload: ResumeMatchRequest) -> dict[str, object]:
    job_text = payload.job_text.strip()
    resume_text = payload.resume_text.strip()
    if not job_text:
        raise HTTPException(status_code=400, detail="Job description text is empty.")
    if not resume_text:
        raise HTTPException(status_code=400, detail="Resume text is empty.")

    try:
        return match_resume_to_job(
            job_text=job_text,
            resume_text=resume_text,
            threshold=payload.threshold,
            top_k=payload.top_k,
            min_predictions=payload.min_predictions,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/{path:path}", include_in_schema=False)
def frontend(path: str) -> Response:
    if path.startswith("api/"):
        raise HTTPException(status_code=404, detail="Not found.")
    if path in {"docs", "redoc", "openapi.json"}:
        raise HTTPException(status_code=404, detail="Not found.")

    return frontend_response(path)


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
