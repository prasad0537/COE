from __future__ import annotations

import argparse
import json
import pickle
from pathlib import Path

import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, hamming_loss
from sklearn.model_selection import train_test_split
from sklearn.multiclass import OneVsRestClassifier
from sklearn.preprocessing import MultiLabelBinarizer

from common import DEFAULT_DATASET_PATH, DEFAULT_LEXICON_PATH, DEFAULT_METRICS_PATH, DEFAULT_MODEL_PATH, DEFAULT_MODEL_PKL_PATH, ensure_project_dirs, load_lexicon, read_jsonl
from prepare_dataset import build_dataset


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train a multi-label skill classifier.")
    parser.add_argument(
        "--dataset",
        type=Path,
        default=DEFAULT_DATASET_PATH,
        help="Path to the JSONL dataset.",
    )
    parser.add_argument(
        "--lexicon",
        type=Path,
        default=DEFAULT_LEXICON_PATH,
        help="Path to the skill lexicon JSON file.",
    )
    parser.add_argument(
        "--model-out",
        type=Path,
        default=DEFAULT_MODEL_PATH,
        help="Path to write the trained model bundle.",
    )
    parser.add_argument(
        "--pkl-out",
        type=Path,
        default=DEFAULT_MODEL_PKL_PATH,
        help="Path to write the trained model bundle as PKL.",
    )
    parser.add_argument(
        "--metrics-out",
        type=Path,
        default=DEFAULT_METRICS_PATH,
        help="Path to write training metrics.",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=None,
        help="Probability threshold for positive labels. If omitted, tune on the holdout split.",
    )
    parser.add_argument(
        "--test-size",
        type=float,
        default=0.2,
        help="Holdout split size.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed.",
    )
    parser.add_argument(
        "--samples-per-skill",
        type=int,
        default=24,
        help="If the dataset is missing, generate this many synthetic records per skill.",
    )
    return parser.parse_args()


def ensure_positive_predictions(probabilities: np.ndarray, predictions: np.ndarray) -> np.ndarray:
    adjusted = predictions.copy()
    for index, row in enumerate(adjusted):
        if row.sum() == 0:
            best_label = int(np.argmax(probabilities[index]))
            row[best_label] = 1
    return adjusted


def select_threshold(probabilities: np.ndarray, y_true: np.ndarray) -> tuple[float, np.ndarray]:
    candidates = [round(value, 2) for value in np.arange(0.05, 0.45, 0.05)]
    best_threshold = candidates[0]
    best_predictions = ensure_positive_predictions(probabilities, (probabilities >= best_threshold).astype(int))
    best_score = f1_score(y_true, best_predictions, average="micro", zero_division=0)

    for threshold in candidates[1:]:
        predictions = ensure_positive_predictions(probabilities, (probabilities >= threshold).astype(int))
        score = f1_score(y_true, predictions, average="micro", zero_division=0)
        if score > best_score:
            best_threshold = threshold
            best_predictions = predictions
            best_score = score

    return float(best_threshold), best_predictions


def load_or_create_dataset(dataset_path: Path, lexicon: list[dict[str, object]], samples_per_skill: int, seed: int) -> list[dict[str, object]]:
    if dataset_path.exists():
        return read_jsonl(dataset_path)

    records = build_dataset(lexicon=lexicon, samples_per_skill=samples_per_skill, seed=seed)
    from common import write_jsonl

    write_jsonl(records, dataset_path)
    return records


def main() -> int:
    args = parse_args()
    ensure_project_dirs()

    lexicon = load_lexicon(args.lexicon)
    records = load_or_create_dataset(args.dataset, lexicon, args.samples_per_skill, args.seed)

    texts = [str(record["text"]) for record in records]
    labels = [list(record["skills"]) for record in records]

    vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True)
    label_binarizer = MultiLabelBinarizer()

    x = vectorizer.fit_transform(texts)
    y = label_binarizer.fit_transform(labels)

    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=args.test_size,
        random_state=args.seed,
    )

    classifier = OneVsRestClassifier(
        LogisticRegression(
            max_iter=1200,
            solver="liblinear",
        )
    )
    classifier.fit(x_train, y_train)

    probabilities = classifier.predict_proba(x_test)
    if args.threshold is None:
        threshold, predictions = select_threshold(probabilities, y_test)
    else:
        threshold = float(args.threshold)
        predictions = ensure_positive_predictions(probabilities, (probabilities >= threshold).astype(int))

    metrics = {
        "num_records": len(records),
        "train_size": int(x_train.shape[0]),
        "test_size": int(x_test.shape[0]),
        "num_labels": int(y.shape[1]),
        "threshold": threshold,
        "micro_f1": round(float(f1_score(y_test, predictions, average="micro", zero_division=0)), 4),
        "macro_f1": round(float(f1_score(y_test, predictions, average="macro", zero_division=0)), 4),
        "exact_match_accuracy": round(float(accuracy_score(y_test, predictions)), 4),
        "hamming_loss": round(float(hamming_loss(y_test, predictions)), 4),
    }

    bundle = {
        "model": classifier,
        "vectorizer": vectorizer,
        "label_binarizer": label_binarizer,
        "threshold": threshold,
        "lexicon": lexicon,
        "metrics": metrics,
    }
    joblib.dump(bundle, args.model_out)
    with args.pkl_out.open("wb") as file:
        pickle.dump(bundle, file)
    args.metrics_out.write_text(json.dumps(metrics, indent=2, ensure_ascii=True), encoding="utf-8")

    print(json.dumps(metrics, indent=2, ensure_ascii=True))
    print(f"Saved model to {args.model_out}")
    print(f"Saved PKL model to {args.pkl_out}")
    print(f"Saved metrics to {args.metrics_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
