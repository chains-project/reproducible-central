import matplotlib.pyplot as plt
import numpy as np
import json

with open('java/unreproducible_maven_projects_to_releases.json', 'r') as f:
    data = json.load(f)


without_release = 0
partial_artifact = 0
without_release_l = []
partial_artifact_l= []
total_artifacts = 0
percentages = []
gav_counts = {}
unreproducible_artifact_distribution = {}
for maven_project in data:
    for release in maven_project['maven_releases']:
        if release['url'] == None:
            without_release += 1
            without_release_l.append(release['gav'])
            continue
        
        unreproducible_artifacts = [i.replace('.diffoscope.json', '') for i in release['unreproducibleArtifacts']]

        all_artifacts = release['allArtifacts']

        if len(set(unreproducible_artifacts) - set(all_artifacts)) > 0:
            partial_artifact += 1
            partial_artifact_l.append(release['gav'])
            continue
        
        total_artifacts += len(unreproducible_artifacts)
        gav = release["gav"]
        gav_counts[gav] = len(release['unreproducibleArtifacts'])
        percentages.append(len(unreproducible_artifacts)/len(all_artifacts) * 100)

for count in gav_counts.values():
    unreproducible_artifact_distribution[count] = unreproducible_artifact_distribution.get(count, 0) + 1

print(unreproducible_artifact_distribution)
print(f"w/o release: {without_release}")
print(f"partial release: {partial_artifact}")
print(f"Total unreproducible artifacts: {total_artifacts}")

fig, (ax1, ax2) = plt.subplots(nrows=2, sharex=True)


ax1.barh(unreproducible_artifact_distribution.keys(), unreproducible_artifact_distribution.values())

for i in unreproducible_artifact_distribution:
    number_of_unreproducible_artifacts = i
    freq = unreproducible_artifact_distribution[i]

    ax1.text(freq+16, number_of_unreproducible_artifacts-0.2, freq, fontsize=12,)

ax1.set_ylabel('# Unreproducible artifacts')

ax2.hist(percentages, orientation='horizontal')
ax2.set_xlabel('# Maven releases')
ax2.set_ylabel('% Unreproducible artifacts')
fig.align_ylabels()
fig.savefig('descriptive_stats.pdf')