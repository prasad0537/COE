from __future__ import annotations

import argparse
import csv
import json
import random
from collections import Counter
from pathlib import Path

from common import DEFAULT_DATASET_CSV_PATH, DEFAULT_DATASET_PATH, DEFAULT_LEXICON_PATH, ensure_project_dirs, load_lexicon, write_jsonl


ROLE_TITLES = {
    "Programming Language": ["Software Engineer", "Backend Engineer", "Platform Engineer"],
    "Framework/Library": ["Full Stack Engineer", "Application Engineer", "ML Engineer"],
    "Cloud/DevOps": ["Cloud Engineer", "DevOps Engineer", "Infrastructure Engineer"],
    "Database": ["Data Engineer", "Analytics Engineer", "Database Engineer"],
    "Data/AI": ["Data Scientist", "Machine Learning Engineer", "AI Engineer"],
    "Architecture": ["Solutions Architect", "Backend Architect", "Platform Architect"],
    "Testing/Quality": ["QA Engineer", "Software Development Engineer in Test", "Quality Engineer"],
    "Tooling": ["Developer Tools Engineer", "Platform Engineer", "Automation Engineer"],
    "Process": ["Technical Program Manager", "Engineering Manager", "Delivery Lead"],
    "Soft Skill": ["Team Lead", "Engineering Manager", "Product Engineer"],
}

OPENINGS = [
    "We are hiring a {role} to build reliable production systems.",
    "Our team needs a {role} to scale critical business workflows.",
    "This {role} position focuses on building high-impact data products.",
    "The {role} will help modernize our platform and delivery process.",
]

REQUIREMENT_PATTERNS = [
    "Required skills include {skills}.",
    "You must have experience with {skills}.",
    "The role needs hands-on knowledge of {skills}.",
    "Strong experience with {skills} is expected.",
]

RESPONSIBILITY_PATTERNS = [
    "You will design pipelines, support delivery teams, and improve model reliability.",
    "You will partner with product, engineering, and analytics teams on production use cases.",
    "You will work on automation, monitoring, and measurable business outcomes.",
    "You will translate business requirements into deployable technical solutions.",
]

OPTIONAL_PATTERNS = [
    "Nice to have: {skills}.",
    "Preferred experience includes {skills}.",
    "Bonus points if you have worked with {skills}.",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a synthetic multi-label dataset for skill extraction.")
    parser.add_argument(
        "--lexicon",
        type=Path,
        default=DEFAULT_LEXICON_PATH,
        help="Path to the skill lexicon JSON file.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_DATASET_PATH,
        help="Output JSONL dataset path.",
    )
    parser.add_argument(
        "--csv-output",
        type=Path,
        default=DEFAULT_DATASET_CSV_PATH,
        help="Output CSV dataset path.",
    )
    parser.add_argument(
        "--samples-per-skill",
        type=int,
        default=24,
        help="Number of synthetic records to create for each skill.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducible generation.",
    )
    return parser.parse_args()


def choose_surface_form(skill: dict[str, object], rng: random.Random) -> str:
    aliases = [str(alias) for alias in skill.get("aliases", []) if str(alias).strip()]
    choices = [str(skill["name"])] + aliases
    return rng.choice(choices)


def join_items(items: list[str]) -> str:
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return ", ".join(items[:-1]) + f", and {items[-1]}"


def dominant_category(skills: list[dict[str, object]]) -> str:
    counts = Counter(str(skill.get("category", "Uncategorized")) for skill in skills)
    return counts.most_common(1)[0][0]


def build_record(record_id: int, anchor_skill: dict[str, object], lexicon: list[dict[str, object]], rng: random.Random) -> dict[str, object]:
    remaining = [skill for skill in lexicon if skill["name"] != anchor_skill["name"]]
    required_extra_count = rng.randint(2, 4)
    optional_count = rng.randint(1, 2)

    required_skills = [anchor_skill] + rng.sample(remaining, required_extra_count)
    remaining_names = {skill["name"] for skill in required_skills}
    optional_pool = [skill for skill in lexicon if skill["name"] not in remaining_names]
    optional_skills = rng.sample(optional_pool, optional_count)

    category = dominant_category(required_skills)
    role = rng.choice(ROLE_TITLES.get(category, ["Machine Learning Engineer"]))

    required_skill_names = [choose_surface_form(skill, rng) for skill in required_skills]
    optional_skill_names = [choose_surface_form(skill, rng) for skill in optional_skills]

    sentences = [
        rng.choice(OPENINGS).format(role=role),
        rng.choice(REQUIREMENT_PATTERNS).format(skills=join_items(required_skill_names[: max(2, len(required_skill_names) - 1)])),
        rng.choice(REQUIREMENT_PATTERNS).format(skills=join_items(required_skill_names[max(1, len(required_skill_names) // 2) :])),
        rng.choice(RESPONSIBILITY_PATTERNS),
        rng.choice(OPTIONAL_PATTERNS).format(skills=join_items(optional_skill_names)),
    ]

    labels = sorted({str(skill["name"]) for skill in required_skills + optional_skills})
    categories = sorted({str(skill["category"]) for skill in required_skills + optional_skills})

    return {
        "id": f"sample-{record_id:05d}",
        "text": " ".join(sentences),
        "skills": labels,
        "categories": categories,
        "source": "synthetic",
        "anchor_skill": str(anchor_skill["name"]),
        "anchor_category": str(anchor_skill["category"]),
    }


def build_dataset(lexicon: list[dict[str, object]], samples_per_skill: int, seed: int) -> list[dict[str, object]]:
    rng = random.Random(seed)
    records: list[dict[str, object]] = []
    record_id = 1

    for skill in lexicon:
        for _ in range(samples_per_skill):
            records.append(build_record(record_id, skill, lexicon, rng))
            record_id += 1

    rng.shuffle(records)
    return records


def write_dataset_summary(records: list[dict[str, object]], output_path: Path) -> Path:
    skill_counter = Counter()
    category_counter = Counter()
    for record in records:
        skill_counter.update(record["skills"])
        category_counter.update(record["categories"])

    summary = {
        "num_records": len(records),
        "num_unique_skills": len(skill_counter),
        "num_unique_categories": len(category_counter),
        "top_skills": skill_counter.most_common(10),
        "top_categories": category_counter.most_common(10),
    }
    summary_path = output_path.with_name(f"{output_path.stem}_summary.json")
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=True), encoding="utf-8")
    return summary_path


def write_dataset_csv(records: list[dict[str, object]], output_path: Path) -> Path:
    fieldnames = ["id", "text", "skills", "categories", "source", "anchor_skill", "anchor_category"]
    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            writer.writerow(
                {
                    "id": record["id"],
                    "text": record["text"],
                    "skills": "|".join(record["skills"]),
                    "categories": "|".join(record["categories"]),
                    "source": record["source"],
                    "anchor_skill": record["anchor_skill"],
                    "anchor_category": record["anchor_category"],
                }
            )
    return output_path


def main() -> int:
    args = parse_args()
    ensure_project_dirs()
    lexicon = load_lexicon(args.lexicon)
    records = build_dataset(lexicon=lexicon, samples_per_skill=args.samples_per_skill, seed=args.seed)
    count = write_jsonl(records, args.output)
    csv_path = write_dataset_csv(records, args.csv_output)
    summary_path = write_dataset_summary(records, args.output)

    print(f"Generated {count} records.")
    print(f"Dataset: {args.output}")
    print(f"CSV: {csv_path}")
    print(f"Summary: {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
