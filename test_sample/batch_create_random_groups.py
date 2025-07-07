import json
import os
import random
import sys

# Setup path to access your core logic
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.create_user import create_user_group_link

# Load user list: [username, leetcode_id, codeforces_id]
with open("test_sample/testUsers.json", "r") as f:
    users = json.load(f)

random.shuffle(users)

GROUP_SIZE = 4
group_number = 1

# Create groups of 4
for i in range(0, len(users), GROUP_SIZE):
    group_chunk = users[i:i + GROUP_SIZE]

    # Skip if not enough users for a full group
    if len(group_chunk) < GROUP_SIZE:
        print(f"⚠️ Skipping incomplete group of {len(group_chunk)} users.")
        break

    group_name = f"group{group_number}"
    print(f"\n🔧 Creating {group_name} with users: {[u[0] for u in group_chunk]}")

    for idx, (username, lc_handle, cf_handle) in enumerate(group_chunk):
        create_user_group_link(
            username_lc=lc_handle,
            username_cf=cf_handle,
            username=username,
            group_name=group_name,
            create_new_group=(idx == 0)  # First user creates the group
        )

    group_number += 1
