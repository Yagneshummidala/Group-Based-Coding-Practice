import os
import sys
import numpy as np
import math
from collections import defaultdict

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from clustering.generate_features import generate_user_feature_vectors, TAG_LIST, DIFFICULTY_ORDER
from clustering.knn_within_cluster import knn_within_cluster
from utils.load_all_users import load_all_users

def safe_ratio(numerator, denominator):
    return numerator / denominator if denominator > 0 else 0

def generate_insight_for_user(username, k=3):
    username = username.strip().lower()
    user_key = f"{username}::aggregated"
    
    features = generate_user_feature_vectors()
    users = {u["username"].strip().lower(): u for u in load_all_users()}

    if user_key not in features:
        return f"❌ Aggregated feature vector not found for {username}."

    user_vector = features[user_key]
    base_score = user_vector[0]

    top_similars = knn_within_cluster(username, k=k)
    if not top_similars:
        return f"⚠️ No similar users found for {username}."

    better_user = None
    for sim_user, _ in top_similars:
        sim_key = f"{sim_user}::aggregated"
        if sim_key in features and features[sim_key][0] > base_score:
            better_user = sim_user
            break

    if not better_user:
        return f"✅ You are already among the top performers in your cluster!"

    better_vector = features[f"{better_user}::aggregated"]

    # Tag and difficulty suggestions (global)
    tag_diff = np.array(better_vector[1:57]) - np.array(user_vector[1:57])
    diff_diff = np.array(better_vector[57:]) - np.array(user_vector[57:])

    top_tags_to_improve = np.argsort(-tag_diff)[:3]
    tag_suggestions = [TAG_LIST[i] for i in top_tags_to_improve if tag_diff[i] > 0]
    if not tag_suggestions:
        fallback = np.array(better_vector[1:57])
        tag_suggestions = [TAG_LIST[i] for i in np.argsort(-fallback)[:3]]

    top_diffs_to_improve = np.argsort(-diff_diff)[:2]
    diff_suggestions = [DIFFICULTY_ORDER[i].capitalize() for i in top_diffs_to_improve if diff_diff[i] > 0]
    if not diff_suggestions:
        fallback = np.array(better_vector[57:])
        diff_suggestions = [DIFFICULTY_ORDER[i].capitalize() for i in np.argsort(-fallback)[:2]]

    # Platform comparison
    user_obj = users.get(username)
    better_obj = users.get(better_user)
    platforms = user_obj.get("data", {}).get("platforms", {})
    better_platforms = better_obj.get("data", {}).get("platforms", {})

    platform_scores = {}
    for p, pdata in platforms.items():
        total = pdata.get("total_submissions", 0)
        correct = pdata.get("correct_submissions", 0)
        unique = pdata.get("unique_problems_solved", 0)
        acc = safe_ratio(correct, total)
        boost = math.log(1 + unique) / math.log(101)
        platform_scores[p] = acc * boost

    threshold = 0.4
    weak_platforms = [p for p, score in platform_scores.items() if score < threshold]
    strong_platforms = [p for p, score in platform_scores.items() if score >= threshold]

    if not platform_scores:
        platform_suggestion = "⚠️ Platform-wise data not sufficient for platform suggestion."
    elif len(weak_platforms) == 0:
        platform_suggestion = "✅ You are doing well on both platforms!"
    elif len(weak_platforms) == 1:
        platform_suggestion = f"You are performing better on **{strong_platforms[0].title()}**. Consider improving on **{weak_platforms[0].title()}**."
    else:
        platform_suggestion = f"⚠️ Your performance on **{', '.join(p.title() for p in weak_platforms)}** is relatively low."

    # Common platform comparison
    compare_platform = next((p for p in platforms if p in better_platforms), None)

    if compare_platform:
        your_tags = defaultdict(int, platforms[compare_platform].get("tags_summary", {}))
        their_tags = defaultdict(int, better_platforms[compare_platform].get("tags_summary", {}))

        tag_gap = [(tag, their_tags[tag] - your_tags[tag]) for tag in TAG_LIST if their_tags[tag] > your_tags[tag]]
        tag_gap.sort(key=lambda x: -x[1])
        top_tag_gaps = [tag.replace('_', ' ').title() for tag, _ in tag_gap[:3]]

        tag_suggestion_from_peer = (
            f"On **{compare_platform.title()}**, {better_user.title()} practiced these more: {', '.join(top_tag_gaps)}"
            if top_tag_gaps else
            f"{better_user.title()} may not have a big tag advantage, but reviewing their trends can still help."
        )

        your_diff = defaultdict(int, platforms[compare_platform].get("difficulty_summary", {}))
        their_diff = defaultdict(int, better_platforms[compare_platform].get("difficulty_summary", {}))

        diff_gap = [(lvl, their_diff[lvl] - your_diff[lvl]) for lvl in DIFFICULTY_ORDER if their_diff[lvl] > your_diff[lvl]]
        diff_gap.sort(key=lambda x: -x[1])
        top_diff_gaps = [lvl.capitalize() for lvl, _ in diff_gap[:2]]

        diff_suggestion_from_peer = (
            f"Also consider improving in: {', '.join(top_diff_gaps)}"
            if top_diff_gaps else
            f"Try practicing across all difficulty levels for better balance."
        )
    else:
        tag_suggestion_from_peer = "No common platform found for tag comparison."
        diff_suggestion_from_peer = "No common platform found for difficulty comparison."

    # Final insight
    insight = f"""
🔍 Insight for {username.title()}:
- Your accuracy score: {base_score:.3f}
- A similar user ({better_user.title()}) has higher score: {features[f"{better_user}::aggregated"][0]:.3f}
- Suggested topics to focus on: {', '.join(tag_suggestions)}
- Suggested difficulty levels to improve: {', '.join(diff_suggestions)}
- {platform_suggestion}
- {tag_suggestion_from_peer}
- {diff_suggestion_from_peer}
"""
    return insight

if __name__ == "__main__":
    uname = input("Enter username for insight: ").strip()
    print(generate_insight_for_user(uname))
