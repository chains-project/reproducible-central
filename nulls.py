import json

with open('make-release-consistent-file-paths.json', 'r') as f:
    data = json.load(f)

for key, value in data.items():
    for artifact in value:
        if artifact['rebuild'] is None:
            print(key)
