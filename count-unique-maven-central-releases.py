import json
import numpy as np
import matplotlib.pyplot as plt

with open('unreproducible_maven_projects_to_releases.json', 'r') as f:
    input_data = json.load(f)

ga_counts = {}
for item in input_data:
    for release in item["maven_releases"]:
        gav = release["gav"]
        ga = ":".join(gav.split(":")[:2])  # Extract GA by excluding the version
        ga_counts[ga] = ga_counts.get(ga, 0) + 1

print(ga_counts)
# Group by the number of versions (values)
version_distribution = {}
for count in ga_counts.values():
    version_distribution[count] = version_distribution.get(count, 0) + 1

print(version_distribution)

# Prepare data for violin plot
violin_data = []
for version_count, ga_count in version_distribution.items():
    violin_data.extend([version_count] * ga_count)

violin_data.sort()
print(violin_data)

min_value = min(violin_data)
max_value = max(violin_data)
median_value = np.median(violin_data)
mean_value = np.mean(violin_data)

# Create the plot
fig, ax = plt.subplots(figsize=(6, 4))
ax.violinplot([violin_data], orientation='horizontal', showextrema=True, showmeans=True)

# Set labels and title
ax.set_yticks([1, 1.25])
ax.set_yticklabels([f'{min(version_distribution.values())}', f'{max(version_distribution.values())}'])
ax.set_ylabel("# Maven Modules")
ax.set_xlabel("# Versions")

plt.text(max_value*0.92, 1.1, f"Max: {max_value}", fontsize=10, color="red")
plt.text(mean_value*1.2, 1.07, f"Mean: {mean_value:.2f}", fontsize=10, color="blue")
plt.text(median_value, 1.12, f"Median: {median_value}", fontsize=10, color="green")

plt.savefig('number_of_releases_per_maven_module.pdf')