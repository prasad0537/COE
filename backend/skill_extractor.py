#!/usr/bin/env python3
"""
Extract candidate-relevant skills from a job description.

Usage:
  python backend/skill_extractor.py backend/sample_job_description.txt --pretty
  type backend/sample_job_description.txt | python backend/skill_extractor.py --pretty
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Sequence


BASE_DIR = Path(__file__).resolve().parent

REQUIREMENT_CUES = (
    "must",
    "required",
    "requirements",
    "need",
    "needs",
    "experience with",
    "proficient in",
    "hands-on",
    "strong",
    "familiarity with",
    "knowledge of",
)

PREFERENCE_CUES = (
    "preferred",
    "nice to have",
    "plus",
    "bonus",
)


FALLBACK_LEXICON = [
    {"name": "Python", "category": "Programming Language", "aliases": ["python"]},
    {"name": "SQL", "category": "Programming Language", "aliases": ["sql", "postgresql", "mysql"]},
    {"name": "Java", "category": "Programming Language", "aliases": ["java"]},
    {"name": "JavaScript", "category": "Programming Language", "aliases": ["javascript", "js"]},
    {"name": "TypeScript", "category": "Programming Language", "aliases": ["typescript", "ts"]},
    {"name": "React", "category": "Framework/Library", "aliases": ["react", "react.js"]},
    {"name": "Node.js", "category": "Framework/Library", "aliases": ["node", "node.js"]},
    {"name": "AWS", "category": "Cloud/DevOps", "aliases": ["aws", "amazon web services"]},
    {"name": "Docker", "category": "Cloud/DevOps", "aliases": ["docker"]},
    {"name": "Kubernetes", "category": "Cloud/DevOps", "aliases": ["kubernetes", "k8s"]},
    {"name": "Git", "category": "Tooling", "aliases": ["git", "github", "gitlab"]},
    {"name": "REST APIs", "category": "Architecture", "aliases": ["rest api", "rest apis", "api development"]},
    {"name": "Communication", "category": "Soft Skill", "aliases": ["communication", "communicate"]},
    {"name": "Problem Solving", "category": "Soft Skill", "aliases": ["problem solving", "troubleshooting"]},
]


@dataclass
class SkillMatch:
    name: str
    category: str
    aliases: Sequence[str]
    mentions: int
    requirement_hits: int
    preference_hits: int
    evidence: List[str]

    @property
    def confidence(self) -> float:
        score = 0.25 + (0.12 * min(self.mentions, 4)) + (0.14 * min(self.requirement_hits, 3))
        score -= 0.08 * min(self.preference_hits, 2)
        return max(0.0, min(1.0, round(score, 3)))


def resolve_path(path: str | None) -> Path | None:
    if not path:
        return None

    candidate = Path(path)
    if candidate.is_absolute():
        return candidate

    cwd_candidate = Path.cwd() / candidate
    if cwd_candidate.exists():
        return cwd_candidate

    return BASE_DIR / candidate


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract skills from a job description.")
    parser.add_argument(
        "input_file",
        nargs="?",
        help="Path to a text file containing the job description. If omitted, reads STDIN.",
    )
    parser.add_argument(
        "--lexicon",
        default=str(BASE_DIR / "skills_lexicon.json"),
        help="Path to JSON lexicon file (default: backend/skills_lexicon.json).",
    )
    parser.add_argument(
        "--min-confidence",
        type=float,
        default=0.30,
        help="Only include skills with confidence >= this value. Default: 0.30",
    )
    parser.add_argument(
        "--top-evidence",
        type=int,
        default=2,
        help="Max evidence lines to include per skill. Default: 2",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print output JSON.",
    )
    return parser.parse_args()


def load_lexicon(path: str | None) -> List[Dict[str, object]]:
    resolved = resolve_path(path)
    if resolved and resolved.exists():
        with resolved.open("r", encoding="utf-8") as file:
            payload = json.load(file)
        skills = payload.get("skills", [])
        if not isinstance(skills, list):
            raise ValueError("Lexicon JSON must have a top-level 'skills' list.")
        validated: List[Dict[str, object]] = []
        for item in skills:
            if not isinstance(item, dict):
                continue
            name = item.get("name")
            category = item.get("category", "Uncategorized")
            aliases = item.get("aliases", [])
            if not name or not isinstance(aliases, list):
                continue
            validated.append(
                {
                    "name": str(name),
                    "category": str(category),
                    "aliases": [str(alias) for alias in aliases if str(alias).strip()],
                }
            )
        if validated:
            return validated
    return FALLBACK_LEXICON


def read_input_text(input_file: str | None) -> str:
    if input_file:
        resolved = resolve_path(input_file)
        if resolved is None:
            return ""
        return resolved.read_text(encoding="utf-8")
    return sys.stdin.read()


def normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def split_sentences(text: str) -> List[str]:
    rough = re.split(r"(?<=[.!?])\s+|\n+", text)
    return [normalize_space(sentence) for sentence in rough if normalize_space(sentence)]


def count_alias_matches(text_lower: str, alias: str) -> int:
    pattern = r"(?<!\w)" + re.escape(alias.lower()) + r"(?!\w)"
    return len(re.findall(pattern, text_lower))


def sentence_contains_alias(sentence_lower: str, aliases: Iterable[str]) -> bool:
    for alias in aliases:
        pattern = r"(?<!\w)" + re.escape(alias.lower()) + r"(?!\w)"
        if re.search(pattern, sentence_lower):
            return True
    return False


def extract_skills(
    text: str,
    lexicon: Sequence[Dict[str, object]],
    min_confidence: float,
    top_evidence: int,
) -> List[SkillMatch]:
    text_lower = text.lower()
    sentences = split_sentences(text)
    sentence_lower = [sentence.lower() for sentence in sentences]

    matches: List[SkillMatch] = []
    for skill in lexicon:
        name = str(skill["name"])
        category = str(skill.get("category", "Uncategorized"))
        aliases = [alias.lower() for alias in skill.get("aliases", []) if isinstance(alias, str)]
        if not aliases:
            continue

        mentions = sum(count_alias_matches(text_lower, alias) for alias in aliases)
        if mentions == 0:
            continue

        evidence: List[str] = []
        requirement_hits = 0
        preference_hits = 0
        for raw_sentence, lower_sentence in zip(sentences, sentence_lower):
            if not sentence_contains_alias(lower_sentence, aliases):
                continue
            evidence.append(raw_sentence)
            if any(cue in lower_sentence for cue in REQUIREMENT_CUES):
                requirement_hits += 1
            if any(cue in lower_sentence for cue in PREFERENCE_CUES):
                preference_hits += 1

        seen = set()
        unique_evidence: List[str] = []
        for line in evidence:
            if line not in seen:
                unique_evidence.append(line)
                seen.add(line)

        match = SkillMatch(
            name=name,
            category=category,
            aliases=aliases,
            mentions=mentions,
            requirement_hits=requirement_hits,
            preference_hits=preference_hits,
            evidence=unique_evidence[: max(1, top_evidence)],
        )
        if match.confidence >= min_confidence:
            matches.append(match)

    matches.sort(key=lambda match: (-match.confidence, -match.mentions, match.name))
    return matches


def build_output(matches: Sequence[SkillMatch]) -> Dict[str, object]:
    category_counts = Counter(match.category for match in matches)
    confidence_buckets = defaultdict(int)

    for match in matches:
        if match.confidence >= 0.75:
            confidence_buckets["high"] += 1
        elif match.confidence >= 0.50:
            confidence_buckets["medium"] += 1
        else:
            confidence_buckets["low"] += 1

    return {
        "summary": {
            "total_skills": len(matches),
            "by_category": dict(sorted(category_counts.items(), key=lambda item: (-item[1], item[0]))),
            "confidence_buckets": dict(confidence_buckets),
        },
        "skills": [
            {
                "name": match.name,
                "category": match.category,
                "mentions": match.mentions,
                "confidence": match.confidence,
                "evidence": match.evidence,
            }
            for match in matches
        ],
    }


def main() -> int:
    args = parse_args()
    text = read_input_text(args.input_file)
    if not text.strip():
        print("Input is empty. Provide a file path or pipe job description text to STDIN.", file=sys.stderr)
        return 1

    lexicon = load_lexicon(args.lexicon)
    matches = extract_skills(
        text=text,
        lexicon=lexicon,
        min_confidence=args.min_confidence,
        top_evidence=args.top_evidence,
    )
    output = build_output(matches)
    if args.pretty:
        print(json.dumps(output, indent=2, ensure_ascii=True))
    else:
        print(json.dumps(output, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
