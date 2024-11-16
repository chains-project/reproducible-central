import os
import json

# Directory containing the JSON files
base_dir = "results"

# Initialize counters and lists for GAVs
gavs_all_0 = []
gavs_failed = []  # Includes all GAVs with jNorm 1 or jNorm 2

# Counters for artifact counts by jNorm value
artifact_counts = {0: 0, 1: 0, 2: 0}

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

            # Update artifact counts
            for jNorm in jNorm_values:
                if jNorm in artifact_counts:
                    artifact_counts[jNorm] += 1

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

