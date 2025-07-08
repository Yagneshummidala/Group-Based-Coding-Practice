import os
import sys
import numpy as np
import json
from sklearn.metrics.pairwise import cosine_similarity

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from clustering.generate_features import generate_user_feature_vectors
from utils.load_all_users import load_all_users

CLUSTERS_FILE = os.path.join(os.path.dirname(__file__), 'clusters.json')

def load_cluster_assignments():
    with open(CLUSTERS_FILE, 'r') as f:
        return json.load(f)

def compute_cluster_centroids(features, clusters):
    centroids = {}
    for cluster_id, members in clusters.items():
        vectors = []
        for u in members:
            key = f"{u.strip().lower()}::aggregated"
            if key in features:
                vectors.append(features[key])
        if vectors:
            centroids[cluster_id] = np.mean(vectors, axis=0)
    return centroids

def knn_within_cluster(username, k=3):
    username = username.strip().lower()
    user_key = f"{username}::aggregated"

    features = generate_user_feature_vectors()
    clusters = load_cluster_assignments()

    if user_key not in features:
        print(f"❌ Feature vector not found for {username}")
        return []

    # Find user's cluster
    user_cluster = None
    for cid, members in clusters.items():
        if username in [m.strip().lower() for m in members]:
            user_cluster = cid
            break

    if not user_cluster:
        print(f"❌ Cluster assignment not found for {username}")
        return []

    # Try same-cluster KNN
    user_vector = np.array(features[user_key]).reshape(1, -1)
    same_cluster_users = [
        u.strip().lower() for u in clusters[user_cluster]
        if u.strip().lower() != username and f"{u.strip().lower()}::aggregated" in features
    ]

    if len(same_cluster_users) >= k:
        similarities = []
        for u in same_cluster_users:
            vec = np.array(features[f"{u}::aggregated"]).reshape(1, -1)
            score = cosine_similarity(user_vector, vec)[0][0]
            similarities.append((u, score))
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:k]

    # Fallback: find nearest cluster using centroid similarity
    print(f"⚠️ Not enough users in cluster {user_cluster}. Falling back to nearest cluster...")
    centroids = compute_cluster_centroids(features, clusters)
    user_centroid = centroids.get(user_cluster)
    if user_centroid is None:
        print("❌ Could not compute centroid for user's cluster.")
        return []

    best_cluster = None
    best_score = -1
    for cid, centroid in centroids.items():
        if cid == user_cluster:
            continue
        score = cosine_similarity(user_centroid.reshape(1, -1), centroid.reshape(1, -1))[0][0]
        if score > best_score:
            best_score = score
            best_cluster = cid

    if not best_cluster:
        print("❌ Could not find a suitable fallback cluster.")
        return []

    print(f"➡️ Fallback to nearest cluster: {best_cluster} (similarity: {best_score:.4f})")
    fallback_users = [
        u.strip().lower() for u in clusters[best_cluster]
        if f"{u.strip().lower()}::aggregated" in features
    ]

    similarities = []
    for u in fallback_users:
        vec = np.array(features[f"{u}::aggregated"]).reshape(1, -1)
        score = cosine_similarity(user_vector, vec)[0][0]
        similarities.append((u, score))

    similarities.sort(key=lambda x: x[1], reverse=True)
    return similarities[:k]

print(knn_within_cluster("kurva_ravi_shanker"))