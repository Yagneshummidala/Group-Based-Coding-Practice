import sys
import os
import json

# Add parent directory to sys.path to access scrapers and utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scrapers.aggregate import build_user_profile
from utils.normalizer import process_aggregation_of_data

def update_user_in_group(username: str, groupname: str):
    group_file_path = os.path.join("groups", f"{groupname}.json")

    if not os.path.exists(group_file_path):
        print(f"❌ Group '{groupname}' does not exist.")
        return

    with open(group_file_path, "r") as f:
        group_data = json.load(f)

    if username not in group_data["users"]:
        print(f"❌ User '{username}' not found in group '{groupname}'.")
        return

    # Get platform handles from stored data
    lc_handle = group_data["users"][username]["leetcode"]
    cf_handle = group_data["users"][username]["codeforces"]

    # Rebuild user profile
    try:
        updated_user_profile = build_user_profile(lc_handle, cf_handle, username, groupname)
    except Exception as e:
        print(f"❌ Failed to update user '{username}': {e}")
        return

    # Update only the user's data block
    group_data["users"][username]["data"] = updated_user_profile["data"]

    # Recompute totalData from all users
    users = group_data["users"].values()
    user_list = list(users)
    first = user_list[0]["data"]
    recomputed_total = {
        "platforms": first["platforms"],
        "aggregated_data": first["aggregated_data"]
    }

    for u in user_list[1:]:
        recomputed_total = {
            "platforms": {
                "leetcode": process_aggregation_of_data(
                    recomputed_total["platforms"]["leetcode"],
                    u["data"]["platforms"]["leetcode"]
                ),
                "codeforces": process_aggregation_of_data(
                    recomputed_total["platforms"]["codeforces"],
                    u["data"]["platforms"]["codeforces"]
                )
            },
            "aggregated_data": process_aggregation_of_data(
                recomputed_total["aggregated_data"],
                u["data"]["aggregated_data"]
            )
        }

    group_data["totalData"] = recomputed_total

    # Save updated group JSON
    with open(group_file_path, "w") as f:
        json.dump(group_data, f, indent=4)

    print(f"✅ User '{username}' updated in group '{groupname}' and group totals recomputed.")


# --- Example usage ---
if __name__ == "__main__":
    update_user_in_group("yagnesh", "testgroup2")
