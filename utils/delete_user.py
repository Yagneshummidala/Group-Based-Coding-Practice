import sys
import os
import json

# Add project root to sys.path to allow relative imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.normalizer import process_aggregation_of_data

def delete_user_from_group(username: str, groupname: str):
    group_file_path = os.path.join("groups", f"{groupname}.json")

    # Step 1: Check if group exists
    if not os.path.exists(group_file_path):
        print(f"❌ Group '{groupname}' does not exist.")
        return

    # Step 2: Load group data
    with open(group_file_path, 'r') as f:
        group_data = json.load(f)

    # Step 3: Check if user exists in the group
    if username not in group_data["users"]:
        print(f"❌ User '{username}' is not a member of group '{groupname}'.")
        return

    # Step 4: Remove user
    del group_data["users"][username]
    group_data["groupMembers"].remove(username)
    group_data["groupSize"] -= 1

    # Step 5: If no users remain, delete the group file
    if group_data["groupSize"] == 0:
        os.remove(group_file_path)
        print(f"🗑️ Group '{groupname}' has no users left and was deleted.")
        return

    # Step 6: Recalculate totalData
    users = list(group_data["users"].values())
    new_total = users[0]
    for user in users[1:]:
        new_total = {
            "platforms": {
                "leetcode": process_aggregation_of_data(
                    new_total["platforms"]["leetcode"],
                    user["platforms"]["leetcode"]
                ),
                "codeforces": process_aggregation_of_data(
                    new_total["platforms"]["codeforces"],
                    user["platforms"]["codeforces"]
                )
            },
            "aggregated_data": process_aggregation_of_data(
                new_total["aggregated_data"],
                user["aggregated_data"]
            )
        }
    group_data["totalData"] = new_total

    # Step 7: Save updated group JSON
    with open(group_file_path, 'w') as f:
        json.dump(group_data, f, indent=4)

    print(f"✅ User '{username}' removed from group '{groupname}'")


# --- Example usage ---
if __name__ == "__main__":
    delete_user_from_group("yagnesh", "testgroup2")
