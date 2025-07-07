import os
import json

def load_all_users():
    groups_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'groups'))
    all_users = []

    for filename in os.listdir(groups_dir):
        if filename.endswith('.json'):
            group_path = os.path.join(groups_dir, filename)

            with open(group_path, 'r') as f:
                group_data = json.load(f)

            users_dict = group_data.get('users', {})

            if isinstance(users_dict, dict):
                for username, user_data in users_dict.items():
                    if 'data' in user_data and 'aggregated_data' in user_data['data']:
                        user_data["username"] = username  # add username to the object
                        all_users.append(user_data)
                    else:
                        print(f"⚠️ Skipping invalid user: {username} in {filename}")
            else:
                print(f"⚠️ 'users' field is not a dict in {filename}, skipping.")

    print(f"✅ Loaded {len(all_users)} valid users from all group files.")
    return all_users

# Test run
if __name__ == "__main__":
    users = load_all_users()
    print(json.dumps(users, indent=2))
