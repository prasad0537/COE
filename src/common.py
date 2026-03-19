from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable


BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"
MODELS_DIR = BASE_DIR / "models"

DEFAULT_LEXICON_PATH = RAW_DATA_DIR / "skills_lexicon.json"
DEFAULT_SAMPLE_TEXT_PATH = RAW_DATA_DIR / "sample_job_description.txt"
DEFAULT_DATASET_PATH = PROCESSED_DATA_DIR / "job_skill_dataset.jsonl"
DEFAULT_DATASET_CSV_PATH = PROCESSED_DATA_DIR / "job_skill_dataset.csv"
DEFAULT_MODEL_PATH = MODELS_DIR / "skill_classifier.joblib"
DEFAULT_MODEL_PKL_PATH = MODELS_DIR / "skill_classifier.pkl"
DEFAULT_METRICS_PATH = MODELS_DIR / "training_metrics.json"


def ensure_project_dirs() -> None:
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)


def load_lexicon(path: Path | str = DEFAULT_LEXICON_PATH) -> list[dict[str, object]]:
    path = Path(path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    skills = payload.get("skills", [])
    if not isinstance(skills, list):
        raise ValueError("Lexicon JSON must contain a top-level 'skills' list.")

    validated: list[dict[str, object]] = []
    for item in skills:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name", "")).strip()
        if not name:
            continue
        category = str(item.get("category", "Uncategorized")).strip() or "Uncategorized"
        aliases = [str(alias).strip() for alias in item.get("aliases", []) if str(alias).strip()]
        validated.append(
            {
                "name": name,
                "category": category,
                "aliases": aliases,
            }
        )
    if not validated:
        raise ValueError(f"No valid skills found in lexicon: {path}")
    return validated


def write_jsonl(records: Iterable[dict[str, object]], path: Path | str) -> int:
    path = Path(path)
    count = 0
    with path.open("w", encoding="utf-8") as file:
        for record in records:
            file.write(json.dumps(record, ensure_ascii=True) + "\n")
            count += 1
    return count


def read_jsonl(path: Path | str) -> list[dict[str, object]]:
    path = Path(path)
    rows: list[dict[str, object]] = []
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def slugify(text: str) -> str:
    cleaned = "".join(char.lower() if char.isalnum() else "-" for char in text)
    while "--" in cleaned:
        cleaned = cleaned.replace("--", "-")
    return cleaned.strip("-")
