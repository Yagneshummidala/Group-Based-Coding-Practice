import os
import sys
import json
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from clustering.generate_features import generate_user_feature_vectors
from clustering.kmeans_clustering import DEFAULT_NUM_CLUSTERS
from utils.load_all_users import load_all_users

CLUSTERS_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'clustering', 'clusters.json'))
OUTPUT_PNG = os.path.abspath(os.path.join(os.path.dirname(__file__), 'cluster_plot.png'))

def load_cluster_assignments():
    with open(CLUSTERS_FILE, 'r') as f:
        return json.load(f)

def build_180d_vectors():
    full_feature_map = generate_user_feature_vectors()
    user_set = set()

    for key in full_feature_map:
        if "::" in key:
            user_set.add(key.split("::")[0])

    vectors = {}
    for username in user_set:
        agg = full_feature_map.get(f"{username}::aggregated", [0]*60)
        lc = full_feature_map.get(f"{username}::leetcode", [0]*60)
        cf = full_feature_map.get(f"{username}::codeforces", [0]*60)
        vectors[username] = agg + lc + cf

    return vectors

def reduce_dimensions(vectors, method='pca'):
    X = np.array(list(vectors.values()))
    if method == 'tsne':
        reducer = TSNE(n_components=2, random_state=42, perplexity=30)
    else:
        reducer = PCA(n_components=2)
    return reducer.fit_transform(X)

def plot_clusters():
    cluster_map = load_cluster_assignments()
    vectors_180d = build_180d_vectors()
    full_feature_map = generate_user_feature_vectors()

    usernames = []
    labels = []
    cluster_scores = {}

    for cluster_id, users in cluster_map.items():
        cluster_scores[cluster_id] = []
        for uname in users:
            uname = uname.strip().lower()
            if uname in vectors_180d:
                usernames.append(uname)
                labels.append(cluster_id)
                score = full_feature_map.get(f"{uname}::aggregated", [0])[0]
                cluster_scores[cluster_id].append((uname, score))

    vectors_filtered = {u: vectors_180d[u] for u in usernames}
    reduced = reduce_dimensions(vectors_filtered, method='pca')

    cluster_ids = sorted(set(labels))
    label_map = {cid: idx for idx, cid in enumerate(cluster_ids)}
    numeric_labels = [label_map[l] for l in labels]

    # Prepare data for centroids
    X = np.array(list(vectors_filtered.values()))
    reduced_dict = dict(zip(usernames, reduced))
    cluster_points = {cid: [] for cid in cluster_ids}
    for uname, label in zip(usernames, labels):
        cluster_points[label].append(reduced_dict[uname])
    centroids = {cid: np.mean(cluster_points[cid], axis=0) for cid in cluster_ids}

    # Start plotting
    plt.figure(figsize=(10, 6))
    scatter = plt.scatter(reduced[:, 0], reduced[:, 1], c=numeric_labels, cmap='tab10', s=40, alpha=0.8)

    # Plot centroids
    for cid, coord in centroids.items():
        plt.scatter(coord[0], coord[1], marker='*', s=200, c='black', edgecolors='white', label=f"{cid} center")

    # Label top performer in each cluster
    for cluster_id in cluster_ids:
        top_users = sorted(cluster_scores[cluster_id], key=lambda x: -x[1])[:1]
        for uname, score in top_users:
            x, y = reduced_dict[uname]
            plt.annotate(uname, (x, y), fontsize=8, weight='bold', xytext=(5, 5), textcoords='offset points')

    plt.title("User Clusters (180D Feature Vector Reduced to 2D)")
    plt.xlabel("Component 1")
    plt.ylabel("Component 2")
    plt.colorbar(scatter, ticks=range(len(cluster_ids)), label='Cluster ID')
    plt.tight_layout()
    plt.savefig(OUTPUT_PNG)
    plt.show()
    print(f"✅ Cluster plot saved as: {OUTPUT_PNG}")

if __name__ == "__main__":
    plot_clusters()
