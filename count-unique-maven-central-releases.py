import json
from collections import defaultdict
from statistics import mean, median

with open('make-release-consistent.json', 'r') as f:
    gav_map = json.load(f)
    
# Count unique Maven Central releases
unique_maven_central_releases = set()
for artifact in gav_map.keys():
    unique_maven_central_releases.add(':'.join(artifact.split(':')[:2]))

# Count versions per artifact
versions_per_artifact = defaultdict(set)
for gav in gav_map.keys():
    group_id, artifact_id, version = gav.split(':')
    artifact_key = f"{group_id}:{artifact_id}"
    versions_per_artifact[artifact_key].add(version)

# Calculate statistics for versions per artifact
versions_counts = [len(versions) for versions in versions_per_artifact.values()]
mean_versions = mean(versions_counts)
max_versions = max(versions_counts)
min_versions = min(versions_counts)

# Collect all jar sizes (using reference_size)
jar_sizes = []
for artifacts in gav_map.values():
    for artifact in artifacts:
        if artifact['name'].endswith('.jar'):
            jar_sizes.append(artifact['reference_size'])

# Calculate statistics
min_size = min(jar_sizes)
max_size = max(jar_sizes)
median_size = median(jar_sizes)

print(f"Maven central packages: {len(unique_maven_central_releases)}")
print(f"Mean releases per package: {mean_versions:.2f}")
print(f"Max releases per package: {max_versions}")
print(f"Min releases per package: {min_versions}")
print(f"Total releases: {sum(versions_counts)}")
print(f"Median jar size: {median_size/1024:.2f} KB")
print(f"Max jar size: {max_size/1024:.2f} KB")
print(f"Min jar size: {min_size/1024:.2f} KB")
