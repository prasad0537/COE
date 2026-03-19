from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import joblib
import numpy as np

from common import DEFAULT_MODEL_PATH, DEFAULT_SAMPLE_TEXT_PATH


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Predict skills from job description text with the trained ML model.")
    parser.add_argument(
        "--model",
        type=Path,
        default=DEFAULT_MODEL_PATH,
        help="Path to the trained model bundle.",
    )
    parser.add_argument(
        "--text",
        type=str,
        help="Inline job description text.",
    )
    parser.add_argument(
        "--text-file",
        type=Path,
        default=DEFAULT_SAMPLE_TEXT_PATH,
        help="Path to a text file containing the job description.",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=None,
        help="Optional override for the probability threshold.",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=12,
        help="Maximum number of predicted skills to return.",
    )
    parser.add_argument(
        "--min-predictions",
        type=int,
        default=5,
        help="Pad with the highest remaining scores until this many labels are returned.",
    )
    return parser.parse_args()


def read_input_text(args: argparse.Namespace) -> str:
    if args.text:
        return args.text
    if args.text_file and args.text_file.exists():
        return args.text_file.read_text(encoding="utf-8")
    return sys.stdin.read()


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


def main() -> int:
    args = parse_args()
    text = read_input_text(args).strip()
    if not text:
        print("Input text is empty.", file=sys.stderr)
        return 1

    bundle = joblib.load(args.model)
    vectorizer = bundle["vectorizer"]
    classifier = bundle["model"]
    label_binarizer = bundle["label_binarizer"]
    threshold = float(args.threshold) if args.threshold is not None else float(bundle["threshold"])
    lexicon_by_name = {entry["name"]: entry for entry in bundle["lexicon"]}

    probabilities = classifier.predict_proba(vectorizer.transform([text]))[0]
    order = np.argsort(probabilities)[::-1]
    selected = [int(index) for index in order if probabilities[index] >= threshold][: args.top_k]
    selected = ensure_non_empty_prediction(probabilities, selected)
    selected = pad_predictions(order, selected, args.min_predictions, args.top_k)

    predictions = []
    for index in selected:
        name = str(label_binarizer.classes_[index])
        lexicon_entry = lexicon_by_name.get(name, {})
        predictions.append(
            {
                "name": name,
                "category": str(lexicon_entry.get("category", "Uncategorized")),
                "confidence": round(float(probabilities[index]), 4),
            }
        )

    categories: dict[str, int] = {}
    for prediction in predictions:
        categories[prediction["category"]] = categories.get(prediction["category"], 0) + 1

    output = {
        "summary": {
            "total_predicted_skills": len(predictions),
            "threshold": float(threshold),
            "top_category": max(categories, key=categories.get) if categories else None,
        },
        "predicted_skills": predictions,
    }

    print(json.dumps(output, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
