import json
import re

with open("java/all.json") as f:
    data = json.load(f)

total_artifacts = 0
unreproducible_artifacts = 0
for project in data:
    for release in project["maven_releases"]:
        if "comment" in release:
            if release['comment'] == '.pom artifact in reference is mapped with the jar file in rebuild':
                total_artifacts += len([
                    i for i in release["allArtifacts"]
                    if not re.fullmatch(r"ratis-assembly-.*\.pom", i)
                ])
                unreproducible_artifacts += len([
                    i for i in release["unreproducibleArtifacts"]
                    if not re.fullmatch(r"ratis-assembly-.*\.pom", i)
                ])

            else:   
                continue
        else:
            total_artifacts += len(release["allArtifacts"])
            unreproducible_artifacts += len(release["unreproducibleArtifacts"])


print(f"Total number of artifacts: {total_artifacts}")
print(f"Total number of unreproducible artifacts: {unreproducible_artifacts}")
