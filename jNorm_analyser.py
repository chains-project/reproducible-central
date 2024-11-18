import os
import json
from collections import defaultdict

# Directory containing the JSON files
base_dir = "results"

# Initialize counters and lists for GAVs
gavs_all_0 = []
gavs_failed = []  # Includes all GAVs with jNorm 1 or jNorm 2

# Counters for artifact counts by jNorm value
artifact_counts = {0: 0, 1: 0, 2: 0}
sources_artifact_counts = {0: 0, 1: 0, 2: 0}  # Counts for *sources.jar

# Enumeration of extensions
extension_counts = defaultdict(int)

# Iterate through the directory structure
for root, _, files in os.walk(base_dir):
    for file in files:
        if file == "jNorm_summary.json":
            file_path = os.path.join(root, file)

            # Read and parse the JSON file
            with open(file_path, "r") as f:
                data = json.load(f)

            gav = data["gav"]
            artifacts = data["artifacts"]

            # Track jNorm values for the current GAV
            jNorm_values = [artifact["jNorm"] for artifact in artifacts]

            # Update artifact counts and extensions
            for artifact in artifacts:
                jNorm = artifact["jNorm"]
                artifact_name = artifact["artifact_name"]

                # Update artifact counts by jNorm
                if jNorm in artifact_counts:
                    artifact_counts[jNorm] += 1

                # Check if the artifact is a *sources.jar
                if artifact_name.endswith("sources.jar") and jNorm in sources_artifact_counts:
                    sources_artifact_counts[jNorm] += 1

                # Count the file extension
                _, ext = os.path.splitext(artifact_name)
                extension_counts[ext] += 1

            # Classify GAVs
            if all(jNorm == 0 for jNorm in jNorm_values):
                gavs_all_0.append(gav)
            elif any(jNorm in [1, 2] for jNorm in jNorm_values):
                gavs_failed.append(gav)

# Print results
print("GAVs with all jNorm 0:", len(gavs_all_0))
for gav in gavs_all_0:
    print(gav)

print("\nGAVs with jNorm 1 or 2 (Failed Normalization):", len(gavs_failed))
for gav in gavs_failed:
    print(gav)

print("\nNumber of artifacts with jNorm:")
print("jNorm 0:", artifact_counts[0])
print("jNorm 1:", artifact_counts[1])
print("jNorm 2:", artifact_counts[2])

print("\nNumber of *sources.jar artifacts with jNorm:")
print("jNorm 0:", sources_artifact_counts[0])
print("jNorm 1:", sources_artifact_counts[1])
print("jNorm 2:", sources_artifact_counts[2])

print("\nEnumeration of extensions in artifact names:")
for ext, count in extension_counts.items():
    print(f"{ext}: {count}")
