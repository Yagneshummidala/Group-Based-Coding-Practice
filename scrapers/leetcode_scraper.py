import requests
from collections import Counter

def process_leetcode(username):
    headers = {
        "Content-Type": "application/json",
        "Referer": f"https://leetcode.com/{username}/",
        "User-Agent": "Mozilla/5.0"
    }

    # Submission Stats
    query1 = """query userSessionProgress($username: String!) {
      allQuestionsCount { difficulty count }
      matchedUser(username: $username) {
        submitStats {
          acSubmissionNum { difficulty count submissions }
          totalSubmissionNum { difficulty count submissions }
        }
      }
    }"""
    resp1 = requests.post("https://leetcode.com/graphql", headers=headers, json={
        "operationName": "userSessionProgress", "query": query1, "variables": {"username": username}
    })
    data1 = resp1.json()["data"]["matchedUser"]["submitStats"]
    total_submissions = sum(x["submissions"] for x in data1["totalSubmissionNum"] if x["difficulty"] != "All")
    correct_submissions = sum(x["count"] for x in data1["acSubmissionNum"] if x["difficulty"] != "All")
    wrong_submissions = total_submissions - correct_submissions
    unique_problems_solved = next(x["count"] for x in data1["acSubmissionNum"] if x["difficulty"] == "All")
    difficulty_summary = {
        x["difficulty"]: x["count"] for x in data1["acSubmissionNum"] if x["difficulty"] != "All"
    }

    # Tags Summary
    query2 = """query skillStats($username: String!) {
      matchedUser(username: $username) {
        tagProblemCounts {
          advanced { tagName problemsSolved }
          intermediate { tagName problemsSolved }
          fundamental { tagName problemsSolved }
        }
      }
    }"""
    resp2 = requests.post("https://leetcode.com/graphql", headers=headers, json={"query": query2, "variables": {"username": username}})
    tags_data = resp2.json()["data"]["matchedUser"]["tagProblemCounts"]
    tags_counter = Counter()
    for level in ["fundamental", "intermediate", "advanced"]:
        for tag in tags_data.get(level, []):
            tags_counter[tag["tagName"]] += tag["problemsSolved"]

    # Language Summary
    query3 = """query languageStats($username: String!) {
      matchedUser(username: $username) {
        languageProblemCount {
          languageName
          problemsSolved
        }
      }
    }"""
    resp3 = requests.post("https://leetcode.com/graphql", headers=headers, json={
        "operationName": "languageStats", "query": query3, "variables": {"username": username}
    })
    language_data = resp3.json()["data"]["matchedUser"]["languageProblemCount"]
    language_summary = {x["languageName"]: x["problemsSolved"] for x in language_data}

    return {
        "total_submissions": total_submissions,
        "correct_submissions": correct_submissions,
        "wrong_submissions": wrong_submissions,
        "unique_problems_solved": unique_problems_solved,
        "tags_summary": dict(tags_counter),
        "difficulty_summary": difficulty_summary,
        "language_summary": language_summary
    }
