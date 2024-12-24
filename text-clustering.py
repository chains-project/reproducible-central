import os
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

def load_diffs_from_nested_files(root_directory):
    """
    Recursively load diffs from .diffoscope.json files within a root directory.

    Parameters:
    root_directory (str): Path to the root directory.

    Returns:
    list of tuple: A list of tuples containing filenames and their corresponding unified diffs.
    """
    diffs = []
    for dirpath, _, filenames in os.walk(root_directory):
        for filename in filenames:
            if filename.endswith(".diffoscope.json"):
                filepath = os.path.join(dirpath, filename)
                with open(filepath, 'r', encoding='utf-8') as file:
                    try:
                        data = file.read()
                        diffs.extend([
                            (filepath, data) 
                        ])
                    except json.JSONDecodeError as e:
                        print(f"Failed to parse {filepath}: {e}")
    return diffs

def recurse_over_diffoscope_file(data):
    """
    Recursively extract unified diffs from nested diffoscope JSON data.

    Parameters:
    data (dict): A JSON object.

    Returns:
    list of str: A list of unified diffs.
    """
    all_diffs = []
    if 'details' not in data:
        diff = data.get('unified_diff')
        if diff:
            all_diffs.append(diff)
    else:
        for detail in data.get('details', []):
            all_diffs.extend(recurse_over_diffoscope_file(detail))
    return all_diffs

def cluster_diffs(diffs, n_clusters=5):
    """
    Cluster textual diffs into groups based on similarity.

    Parameters:
    diffs (list of tuple): List of tuples containing filenames and diffs.
    n_clusters (int): Number of clusters to form.

    Returns:
    dict: A dictionary where keys are cluster labels and values are lists of tuples (filename, diff).
    """
    diff_texts = [diff[1] for diff in diffs]
    vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
    tfidf_matrix = vectorizer.fit_transform(diff_texts)

    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    labels = kmeans.fit_predict(tfidf_matrix)

    clustered_diffs = {i: [] for i in range(n_clusters)}
    for label, diff in zip(labels, diffs):
        clustered_diffs[label].append(diff)

    if len(diffs) > 1:
        silhouette_avg = silhouette_score(tfidf_matrix, labels)
        print(f"Silhouette Score: {silhouette_avg:.2f}")

    return clustered_diffs

# Main execution
root_directory = "results"
raw_diffs = load_diffs_from_nested_files(root_directory)
clusters = cluster_diffs(raw_diffs, n_clusters=3)

for cluster_id, cluster_diffs in clusters.items():
    print(f"Cluster {cluster_id}:")
    for filename, diff in cluster_diffs:
        print(f"  - File: {filename}")
        print(f"  - Diff: {diff[:100]}...")  # Print first 100 chars for brevity
