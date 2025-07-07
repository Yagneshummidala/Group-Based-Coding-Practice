from collections import defaultdict

# --- Difficulty Normalization ---
def normalize_difficulty(rating_str):
    try:
        rating = int(rating_str)
        if rating < 1200:
            return "Easy"
        elif rating < 1800:
            return "Medium"
        else:
            return "Hard"
    except ValueError:
        cleaned = rating_str.strip().lower()
        if cleaned in {"easy", "medium", "hard"}:
            return cleaned.capitalize()
        return "Unknown"

# --- Tag Normalization ---
TAG_NORMALIZATION_MAP = {
    "2-sat": {"2-sat"},
    "array": {"array", "arrays"},
    "backtracking": {"backtracking"},
    "binary_indexed_tree": {"binaryindexedtree", "fenwicktree", "binary indexed tree"},
    "binary_search": {"binarysearch", "binary_search", "binary search"},
    "binary_tree": {"binary tree"},
    "bit_manipulation": {"bit", "bitmanipulation", "bit manipulation", "bitmasks"},
    "brute_force": {"bruteforce", "brute_force", "brute force", "counting"},
    "concurrency": {"concurrency"},
    "data_stream": {"data stream"},
    "data_structures": {"datastructures", "data_structures"},
    "database": {"database"},
    "design": {"design"},
    "dfs": {"dfs", "depthfirstsearch", "depth_first_search"},
    "divide_and_conquer": {"divideandconquer", "divide_and_conquer", "divide and conquer"},
    "dp": {"dp", "dynamicprogramming", "dynamic_programming", "memoization"},
    "expression_parsing": {"expression parsing"},
    "fft": {"fft"},
    "game_theory": {"game theory", "games"},
    "geometry": {"geometry"},
    "graph": {
        "graph", "graphs", "dfs and similar", "shortest paths", "topological sort",
        "minimum spanning tree", "strongly connected component", "biconnected component",
        "eulerian circuit", "line sweep", "graph matchings"
    },
    "greedy": {"greedy"},
    "hash_table": {"hashtable", "hash_map", "hash table", "map", "hash function", "hashing"},
    "implementation": {"implementation", "constructive algorithms"},
    "interactive": {"interactive"},
    "iterator": {"iterator"},
    "linked_list": {"linkedlist", "linked_list", "doubly-linked list"},
    "matrix": {"matrix", "matrices"},
    "math": {"math", "mathematics"},
    "meet_in_the_middle": {"meet-in-the-middle"},
    "number_theory": {"number theory", "chinese remainder theorem"},
    "prefix_sum": {"prefix sum"},
    "probability": {"probabilities", "probability", "probability and statistics"},
    "queue": {"queue", "monotonic queue"},
    "quickselect": {"quickselect"},
    "radix_sort": {"radix sort"},
    "random": {"random"},
    "randomized": {"randomized", "reservoir sampling", "rejection sampling", "rolling hash"},
    "recursion": {"recursion"},
    "segment_tree": {"segmenttree", "segment tree"},
    "shell": {"shell"},
    "simulation": {"simulation"},
    "sorting": {"sorting", "sort", "sortings", "bucket sort", "counting sort", "merge sort"},
    "special": {"*special", "brainteaser"},
    "stack": {"stack", "monotonic stack"},
    "string": {"string", "strings", "string matching", "string suffix structures"},
    "suffix_array": {"suffix array"},
    "schedules": {"schedules"},
    "ternary_search": {"ternary search"},
    "tree": {"tree", "trees", "binary search tree"},
    "trie": {"trie"},
    "two_pointers": {"twopointers", "two pointers", "sliding window"},
    "union_find": {"unionfind", "disjointset", "dsu"}
}


def clean_token(token):
    return token.strip().lower().replace(" ", "").replace("-", "").replace("_", "")

def normalize_tag(tag):
    if not tag:
        return "unknown"
    cleaned = clean_token(tag)
    for canonical, variants in TAG_NORMALIZATION_MAP.items():
        if cleaned in variants:
            return canonical
    return cleaned or "unknown"

# --- Language Normalization ---
LANGUAGE_NORMALIZATION_MAP = {
    "c++": {
        "c++", "c++17", "c++14", "c++11", "c++20", "gnu g++17", "gnu g++20", "clang19usingc++23standard",
        "msc++2017", "c++(gcc)", "c++20gcc13-64", "clang", "msvc", "g++", "c++98", "c++03", "c++17gcc7-32"
    },
    "c": {
        "c", "gnu c11", "gnu c99", "c11", "c99", "gcc", "c(gcc)", "gcc14usinggnu11standard"
    },
    "python": {
        "python", "python2", "python3", "python 2.7.18", "python 3.11", "py3", "cpython", "python3.10"
    },
    "java": {
        "java", "openjdk", "openjdk21", "java8", "java11", "java 8", "java 11"
    },
    "javascript": {
        "javascript", "js", "node", "node.js", "node22.14.0"
    },
    "c#": {
        "c#", "csharp", "c#13", ".net", ".net9runtime"
    },
    "ruby": {"ruby", "ruby3.2"},
    "swift": {"swift", "swift6.0"},
    "go": {"go", "golang", "go1.23"},
    "scala": {"scala", "scala3.3.1"},
    "kotlin": {"kotlin", "kotlin1.7", "kotlin2.1.10"},
    "rust": {"rust", "rust1.85.0"},
    "php": {"php", "php8.2"},
    "typescript": {"typescript", "ts", "typescript5.7.3"},
    "racket": {"racket", "racketcsv8.15"},
    "erlang": {"erlang", "erlangotp26"},
    "elixir": {"elixir", "elixir1.17"},
    "dart": {"dart", "dart3.2"},
    "bash": {"bash", "bash5.2.21", "shell"},
    "mysql": {"mysql"},
    "mssql": {"mssql", "sql server"},
    "oracle_sql": {"oracle", "oracle sql"},
    "postgresql": {"postgresql", "postgres"},
    "pandas": {"pandas", "python pandas", "numpy"},
    "react": {"react", "react.js"},
    "vanilla_js": {"vanilla js", "vanillajs"},
}

def normalize_language(lang):
    if not lang:
        return "unknown"
    cleaned = clean_token(lang.replace("(", "").replace(")", ""))
    for canonical, variants in LANGUAGE_NORMALIZATION_MAP.items():
        if cleaned in {clean_token(v.replace("(", "").replace(")", "")) for v in variants}:
            return canonical
    return cleaned or "unknown"

# --- Merge Utilities ---
def merge_and_normalize_dicts(dict1, dict2, normalize_func):
    result = defaultdict(int)
    for d in (dict1, dict2):
        for key, count in d.items():
            norm_key = normalize_func(key)
            result[norm_key] += count
    return dict(result)

def normalize_and_merge_difficulties(dict1, dict2):
    result = defaultdict(int)
    for d in (dict1, dict2):
        for diff, count in d.items():
            norm_diff = normalize_difficulty(diff) if diff.isdigit() else normalize_difficulty(diff)
            result[norm_diff] += count
    return dict(result)

# --- Main Aggregation ---
def process_aggregation_of_data(data_1, data_2):
    return {
        "total_submissions": data_1["total_submissions"] + data_2["total_submissions"],
        "correct_submissions": data_1["correct_submissions"] + data_2["correct_submissions"],
        "wrong_submissions": data_1["wrong_submissions"] + data_2["wrong_submissions"],
        "unique_problems_solved": data_1["unique_problems_solved"] + data_2["unique_problems_solved"],
        "tags_summary": merge_and_normalize_dicts(data_1["tags_summary"], data_2["tags_summary"], normalize_tag),
        "difficulty_summary": normalize_and_merge_difficulties(data_1["difficulty_summary"], data_2["difficulty_summary"]),
        "language_summary": merge_and_normalize_dicts(data_1["language_summary"], data_2["language_summary"], normalize_language),
    }
