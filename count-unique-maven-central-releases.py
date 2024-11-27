import json
from collections import defaultdict
from statistics import mean, median
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

with open('make-release-consistent.json', 'r') as f:
    gav_map = json.load(f)

with open('jar_analysis.json', 'r') as f:
    jar_analysis = json.load(f)


classfile_counts = []
sizes = []

for gav, artifacts in jar_analysis.items():
    total_classfiles = 0
    total_size = 0
    for artifact in artifacts:
        name = artifact['artifactName']
        # Skip source, javadoc and test JARs
        if any(x in name for x in ['-sources.', '-javadoc.', '-tests.', '-test-']):
            continue
        if name.endswith('.jar'):
            total_classfiles += artifact['numberOfClassfiles']
            total_size += artifact['size']
    
    classfile_counts.append(total_classfiles)
    sizes.append(total_size)
    
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

plot_data = {
    'Number of Maven Central Modules': versions_per_artifact.keys(),
    'Number of releases for each maven module': versions_counts,
}

violin_df = pd.DataFrame(plot_data)


plt.figure(figsize=(8, 6))
sns.violinplot(data=violin_df, inner="point")

plt.ylabel("Number of releases")
plt.tight_layout()

# Save plots before showing
plt.savefig('number_of_releases_per_maven_module.svg', format='svg', bbox_inches='tight')
plt.savefig('number_of_releases_per_maven_module.pdf', format='pdf', bbox_inches='tight')


print(f"Maven central packages: {len(unique_maven_central_releases)}")
print(f"Mean releases per package: {mean_versions:.2f}")
print(f"Max releases per package: {max_versions}")
print(f"Min releases per package: {min_versions}")
print(f"Total releases: {sum(versions_counts)}")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

# Plot 1: Number of class files
sns.violinplot(y=classfile_counts, ax=ax1)
ax1.set_title('Number of Class Files per JAR')
ax1.set_ylabel('Number of Class Files')

# Plot 2: JAR sizes
sns.violinplot(y=[s/1024 for s in sizes], ax=ax2)  # Convert to KB
ax2.set_title('JAR Sizes')
ax2.set_ylabel('Size (KB)')

plt.tight_layout()
plt.savefig('jar_metrics_violin.pdf')
plt.savefig('jar_metrics_violin.png')

# Print summary statistics
print(f"Total JARs analyzed: {len(classfile_counts)}")
print(f"Average class files per maven release: {sum(classfile_counts)/len(classfile_counts):.2f}")
print(f"Average JAR size: {sum(sizes)/len(sizes)/1024:.2f} KB")
