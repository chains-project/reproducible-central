import json

with open('make-release-consistent.json', 'r') as f:
    gav_map = json.load(f)

unique_maven_central_releases = set()
for artifact in gav_map.keys():
    unique_maven_central_releases.add(':'.join(artifact.split(':')[:2]))

print(f'{len(unique_maven_central_releases)} unique Maven Central releases found')
