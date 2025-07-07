import requests
from collections import Counter
import sys
import os

# Add utils to path and import normalizer
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'utils')))
from utils.normalizer import normalize_tag, normalize_difficulty, normalize_language

def fetch_cf(handle):
    try:
        resp = requests.get(f"https://codeforces.com/api/user.status?handle={handle}")
        data = resp.json()
        return data["result"] if data.get("status") == "OK" else []
    except Exception as e:
        print("❌ Codeforces fetch error:", e)
        return []

def process_codeforces(handle):
    submissions = fetch_cf(handle)
    total_subs = len(submissions)
    correct_subs = 0
    seen_ids = set()
    tags_counter = Counter()
    difficulty_counter = Counter()
    language_summary = {}

    for sub in submissions:
        verdict = sub.get("verdict", "")
        problem = sub.get("problem", {})
        language = sub.get("programmingLanguage", "")
        pid = f"{problem.get('contestId', '')}{problem.get('index', '')}"

        # Normalize language
        normalized_lang = normalize_language(language)
        language_summary[normalized_lang] = language_summary.get(normalized_lang, 0) + 1

        if verdict == "OK":
            correct_subs += 1
            if pid in seen_ids:
                continue
            seen_ids.add(pid)

            # Normalize tags
            raw_tags = problem.get("tags", [])
            for tag in raw_tags:
                norm_tag = normalize_tag(tag)
                tags_counter[norm_tag] += 1

            # Normalize difficulty
            difficulty = str(problem.get("rating", "None"))
            norm_diff = normalize_difficulty(difficulty)
            difficulty_counter[norm_diff] += 1

    return {
        "total_submissions": total_subs,
        "correct_submissions": correct_subs,
        "wrong_submissions": total_subs - correct_subs,
        "unique_problems_solved": len(seen_ids),
        "tags_summary": dict(tags_counter),
        "difficulty_summary": dict(difficulty_counter),
        "language_summary": language_summary
    }
