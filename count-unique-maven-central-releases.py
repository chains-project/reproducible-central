import json
import numpy as np
import matplotlib.pyplot as plt

from statistics import median, mean

with open('unreproducible_maven_projects_to_releases.json', 'r') as f:
    input_data = json.load(f)


gav_counts = {}
for item in input_data:
    for release in item["maven_releases"]:
        gav = release["gav"]
        gav_counts[gav] = len(release['unreproducible_artifacts'])

unreproducible_artifact_distribution = {}
for count in gav_counts.values():
    unreproducible_artifact_distribution[count] = unreproducible_artifact_distribution.get(count, 0) + 1

print(unreproducible_artifact_distribution)

plt.bar(unreproducible_artifact_distribution.keys(), unreproducible_artifact_distribution.values())

for i in unreproducible_artifact_distribution:
    number_of_unreproducible_artifacts = i
    freq = unreproducible_artifact_distribution[i]

    plt.text(number_of_unreproducible_artifacts-0.15, freq+16, freq, fontsize=12,)

plt.xlabel('# Non-reproducible artifacts')
plt.ylabel('# Maven releases')

plt.savefig('descriptive_stats.pdf')
plt.show()