import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
from sklearn.cluster import KMeans
from clustering.generate_features import generate_user_feature_vectors

# --- Config ---
DEFAULT_NUM_CLUSTERS = 8
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "clusters.json")

# --- Run Clustering on 180D Vectors ---
def run_kmeans_clustering():
    full_feature_map = generate_user_feature_vectors()
    
    # Extract base usernames (before ::platform)
    user_set = set()
    for key in full_feature_map:
        if "::" in key:
            user_set.add(key.split("::")[0])

    usernames = sorted(user_set)
    feature_vectors = []

    for username in usernames:
        agg_vec = full_feature_map.get(f"{username}::aggregated", [0] * 60)
        lc_vec = full_feature_map.get(f"{username}::leetcode", [0] * 60)
        cf_vec = full_feature_map.get(f"{username}::codeforces", [0] * 60)

        # Combine into a single 180D vector
        combined_vector = agg_vec + lc_vec + cf_vec
        feature_vectors.append(combined_vector)

    if not feature_vectors:
        print("❌ No user feature vectors found.")
        return {}

    num_users = len(usernames)
    clusters_to_use = min(DEFAULT_NUM_CLUSTERS, num_users)

    if clusters_to_use < 2:
        print(f"⚠️ Not enough users to perform clustering. At least 2 users are required.")
        return {}

    print(f"🧪 Clustering {num_users} users using 180D vectors into {clusters_to_use} clusters...")

    kmeans = KMeans(n_clusters=clusters_to_use, random_state=42, n_init=10)
    labels = kmeans.fit_predict(feature_vectors)

    cluster_result = {}
    for user, label in zip(usernames, labels):
        cluster_key = f"cluster_{label}"
        cluster_result.setdefault(cluster_key, []).append(user)

    with open(OUTPUT_FILE, "w") as f:
        json.dump(cluster_result, f, indent=2)

    print(f"✅ Clustering complete with {clusters_to_use} clusters. Results saved to: {OUTPUT_FILE}")
    return cluster_result

# --- Optional: Run directly ---
if __name__ == "__main__":
    run_kmeans_clustering()
