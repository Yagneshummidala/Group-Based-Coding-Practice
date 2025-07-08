import os
import numpy as np
import math
from utils.load_all_users import load_all_users

# Fixed tag list used across all platforms
TAG_LIST = [
    '2-sat', 'array', 'backtracking', 'binary_indexed_tree', 'binary_search', 'binary_tree',
    'bit_manipulation', 'brute_force', 'concurrency', 'data_stream', 'data_structures', 'database',
    'design', 'dfs', 'divide_and_conquer', 'dp', 'expression_parsing', 'fft', 'game_theory',
    'geometry', 'graph', 'greedy', 'hash_table', 'implementation', 'interactive', 'iterator',
    'linked_list', 'matrix', 'math', 'meet_in_the_middle', 'number_theory', 'prefix_sum',
    'probability', 'queue', 'quickselect', 'radix_sort', 'random', 'randomized', 'recursion',
    'segment_tree', 'shell', 'simulation', 'sorting', 'special', 'stack', 'string', 'suffix_array',
    'schedules', 'ternary_search', 'tree', 'trie', 'two_pointers', 'union_find'
]

DIFFICULTY_ORDER = ['easy', 'medium', 'hard']

def safe_ratio(numerator, denominator):
    return numerator / denominator if denominator > 0 else 0

def merge_dicts_sum(dicts):
    """Merge multiple dictionaries by summing values of the same keys."""
    from collections import defaultdict
    result = defaultdict(int)
    for d in dicts:
        for key, val in d.items():
            result[key] += val
    return dict(result)

def generate_user_feature_vectors():
    all_users = load_all_users()
    feature_map = {}
    print(f"✅ Loaded {len(all_users)} valid users from all group files.")

    for user in all_users:
        username_raw = user.get("username", "")
        username = username_raw.strip().lower()

        data = user.get("data", {})
        platforms = data.get("platforms", {})
        agg_data = data.get("aggregated_data", {})

        sources = {
            'aggregated': {
                "total_submissions": agg_data.get("total_submissions", 0),
                "correct_submissions": agg_data.get("correct_submissions", 0),
                "unique_problems_solved": agg_data.get("unique_problems_solved", 0),
                "tags_summary": agg_data.get("tags_summary", {}),
                "difficulty_summary": agg_data.get("difficulty_summary", {})
            },
            'leetcode': platforms.get('leetcode', {}),
            'codeforces': platforms.get('codeforces', {})
        }

        # Fallback for aggregated in case fields are missing
        if not sources['aggregated']["total_submissions"]:
            sources['aggregated']["total_submissions"] = sum(p.get("total_submissions", 0) for p in platforms.values())
            sources['aggregated']["correct_submissions"] = sum(p.get("correct_submissions", 0) for p in platforms.values())
            sources['aggregated']["unique_problems_solved"] = sum(p.get("unique_problems_solved", 0) for p in platforms.values())
            sources['aggregated']["tags_summary"] = merge_dicts_sum([p.get("tags_summary", {}) for p in platforms.values()])
            sources['aggregated']["difficulty_summary"] = merge_dicts_sum([p.get("difficulty_summary", {}) for p in platforms.values()])

        for source_name, source_data in sources.items():
            total = source_data.get("total_submissions", 0)
            correct = source_data.get("correct_submissions", 0)
            unique = source_data.get("unique_problems_solved", 0)
            tag_dist = source_data.get("tags_summary", {})
            diff_dist = source_data.get("difficulty_summary", {})

            acc = safe_ratio(correct, total)
            boost = math.log(1 + unique) ** 2
            accuracy_score = acc * boost

            tag_vector = [tag_dist.get(tag, 0) for tag in TAG_LIST]
            diff_vector = [diff_dist.get(diff, 0) for diff in DIFFICULTY_ORDER]

            final_vector = [accuracy_score] + tag_vector + diff_vector
            feature_map[f"{username}::{source_name}"] = final_vector

    print(f"✅ Feature vectors generated for {len(feature_map)} user-platform combinations.")
    return feature_map
