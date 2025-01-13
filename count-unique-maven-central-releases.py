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

# Group by the number of versions (values)
version_distribution = {}
for count in ga_counts.values():
    version_distribution[count] = version_distribution.get(count, 0) + 1


gav_counts = {}
for item in input_data:
    for release in item["maven_releases"]:
        gav = release["gav"]
        gav_counts[gav] = len(release['unreproducible_artifacts'])

unreproducible_artifact_distribution = {}
for count in gav_counts.values():
    unreproducible_artifact_distribution[count] = unreproducible_artifact_distribution.get(count, 0) + 1

print(unreproducible_artifact_distribution)


# Prepare data for violin plot
violin_data = []
for version_count, ga_count in version_distribution.items():
    violin_data.extend([version_count] * ga_count)

violin_data.sort()

violin_data1 = []
for version_count, ga_count in unreproducible_artifact_distribution.items():
    violin_data1.extend([version_count] * ga_count)

violin_data1.sort()
print(violin_data1)

min_value = min(violin_data)
max_value = max(violin_data)
median_value = np.median(violin_data)
mean_value = np.mean(violin_data)

min_value1 = min(violin_data1)
max_value1 = max(violin_data1)
median_value1 = np.median(violin_data1)
mean_value1 = np.mean(violin_data1)

# Create the plot
fig, axs = plt.subplots(nrows=2, ncols=1, figsize=(6, 8))
axs[0].violinplot([violin_data], orientation='horizontal', showextrema=True, showmeans=True)
axs[1].violinplot([violin_data1], orientation='horizontal', showextrema=True, showmeans=True)

# Set labels and title
axs[0].set_yticks([1, 1.25])
axs[0].set_yticklabels([f'{min(version_distribution.values())}', f'{max(version_distribution.values())}'])
axs[0].set_ylabel("# Maven Modules")
axs[0].set_xlabel("# Versions")

axs[1].set_yticks([1, 1.25])
axs[1].set_yticklabels([f'{min(unreproducible_artifact_distribution.values())}', f'{max(unreproducible_artifact_distribution.values())}'])
axs[1].set_ylabel("# Maven Releases")
axs[1].set_xlabel("# Artifacts")

axs[0].text(max_value*0.86, 1.1, f"Max: {max_value}", fontsize=10, color="red")
axs[0].text(mean_value*1.2, 1.07, f"Mean: {mean_value:.2f}", fontsize=10, color="blue")
axs[0].text(median_value, 1.12, f"Median: {median_value}", fontsize=10, color="green")

axs[1].text(max_value1*0.90, 1.1, f"Max: {max_value1}", fontsize=10, color="red")
axs[1].text(mean_value1*1.2, 1.07, f"Mean: {mean_value1:.2f}", fontsize=10, color="blue")
axs[1].text(median_value1, 1.12, f"Median: {median_value1}", fontsize=10, color="green")

plt.savefig('number_of_releases_per_maven_module.pdf')