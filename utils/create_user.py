import sys
import os
import json

# Add parent directory to sys.path to access scrapers and utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scrapers.aggregate import build_user_profile
from utils.normalizer import process_aggregation_of_data

def create_user_group_link(username_lc: str, username_cf: str, username: str, group_name: str, create_new_group: bool):
    group_file_path = os.path.join("groups", f"{group_name}.json")

    # Step 1: Load or initialize group JSON
    if create_new_group:
        if os.path.exists(group_file_path):
            print(f"❌ Group '{group_name}' already exists. Choose a different name or join instead.")
            return
        group_data = {
            "groupname": group_name.capitalize(),
            "groupSize": 0,
            "groupMembers": [],
            "totalData": {
                "platforms": {
                    "leetcode": {},
                    "codeforces": {}
                },
                "aggregated_data": {}
            },
            "users": {}
        }
    else:
        if not os.path.exists(group_file_path):
            print(f"❌ Group '{group_name}' does not exist. Use create_new_group=True to create it.")
            return
        with open(group_file_path, 'r') as f:
            group_data = json.load(f)

        if username in group_data["groupMembers"]:
            print(f"⚠️ User '{username}' is already a member of group '{group_name}'")
            return

    # Step 2: Build user profile
    try:
        user_profile = build_user_profile(username_lc, username_cf, username, group_name)
        if not isinstance(user_profile, dict) or not user_profile:
            print(f"❌ Failed to fetch valid data for user: {username}")
            return
    except Exception as e:
        print(f"❌ Error while building user profile: {e}")
        return

    # Step 3: Add user data with handles
    group_data["groupMembers"].append(username)
    group_data["groupSize"] += 1
    group_data["users"][username] = {
        "leetcode": username_lc,
        "codeforces": username_cf,
        "data": user_profile["data"]
    }

    user_data = user_profile["data"]

    # Step 4: Update totalData
    if group_data["groupSize"] == 1:
        group_data["totalData"] = {
            "platforms": user_data["platforms"],
            "aggregated_data": user_data["aggregated_data"]
        }
    else:
        group_data["totalData"] = {
            "platforms": {
                "leetcode": process_aggregation_of_data(
                    group_data["totalData"]["platforms"]["leetcode"],
                    user_data["platforms"]["leetcode"]
                ),
                "codeforces": process_aggregation_of_data(
                    group_data["totalData"]["platforms"]["codeforces"],
                    user_data["platforms"]["codeforces"]
                )
            },
            "aggregated_data": process_aggregation_of_data(
                group_data["totalData"]["aggregated_data"],
                user_data["aggregated_data"]
            )
        }

    # Step 5: Save updated group JSON
    os.makedirs("groups", exist_ok=True)  # Ensure the 'groups' folder exists
    with open(group_file_path, "w") as f:
        json.dump(group_data, f, indent=4)

    # Step 6: Final confirmation
    if create_new_group:
        print(f"✅ New group '{group_name}' created with user '{username}'")
    else:
        print(f"✅ User '{username}' added to group '{group_name}'")


# --- Example usage ---
if __name__ == "__main__":
    # Toggle True for new group, False to join existing
    create_user_group_link('nithin6743', 'nithin6743', 'nithin', 'testgroup1', True)
