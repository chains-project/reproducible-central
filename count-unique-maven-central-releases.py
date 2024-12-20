import json
from collections import defaultdict
from statistics import median
import seaborn as sns
import matplotlib.pyplot as plt

# Read the JSON file
with open('make-release-consistent.json', 'r') as f:
    gav_map = json.load(f)

# Count versions per artifact
versions_per_artifact = defaultdict(set)
for gav in gav_map.keys():
    group_id, artifact_id, version = gav.split(':')
    artifact_key = f"{group_id}:{artifact_id}"
    versions_per_artifact[artifact_key].add(version)

# Get the count of versions for each artifact
versions_counts = [len(versions) for versions in versions_per_artifact.values()]

# Create the plot with adjusted figure size
plt.figure(figsize=(8, 6))
violin = sns.violinplot(x=versions_counts, orient='h', inner="point")

# Calculate and add median line
median_value = median(versions_counts)
plt.axvline(x=median_value, color='r', linestyle='--', alpha=0.5)
plt.text(median_value * 1.1, 0.02, f'Median: {median_value:.1f}', 
         color='r', horizontalalignment='left', verticalalignment='bottom',
         rotation=0)

plt.xlabel("Number of versions per Maven module")
plt.tight_layout()

# Save plots
plt.savefig('number_of_releases_per_maven_module.svg', format='svg', bbox_inches='tight')
plt.savefig('number_of_releases_per_maven_module.pdf', format='pdf', bbox_inches='tight')

# Print some statistics
print(f"Total Maven modules: {len(versions_per_artifact)}")
print(f"Average versions per module: {sum(versions_counts)/len(versions_counts):.2f}")
print(f"Maximum versions for a module: {max(versions_counts)}")
print(f"Minimum versions for a module: {min(versions_counts)}")