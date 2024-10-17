#!/usr/bin/env python3

from pathlib import Path
import os
import json
import csv

count_of_tools = {'procyon': {}, 'javap': {}}

def process_details(details, group_id, artifact_id, count_of_tools, version, diffoscope_file):
    for detail in details:
        source1 = detail.get('source1', '')
        source2 = detail.get('source2', '')
        unified_diff = detail.get('unified_diff', '')

        for tool in ['procyon', 'javap']:
            if tool in source1 or tool in source2:
                key = f"{group_id}:{artifact_id}:{version}"
                if key not in count_of_tools[tool]:
                    count_of_tools[tool][key] = {'diffs': set(), 'file': diffoscope_file}
                count_of_tools[tool][key]['diffs'].add(unified_diff)
        
        # Recursively process nested details
        if 'details' in detail:
            process_details(detail['details'], group_id, artifact_id, count_of_tools, version, diffoscope_file)

def analyze_diffoscope(diffoscope_file):
    with open(diffoscope_file, 'r') as file:
        data = json.load(file)

    diffoscope_file = Path(diffoscope_file)
    version = diffoscope_file.parent.name
    artifact_id = diffoscope_file.parent.parent.name
    group_id = diffoscope_file.parent.parent.parent.name
    
    if 'details' in data:
        process_details(data['details'], group_id, artifact_id, count_of_tools, version, str(diffoscope_file))
    else:
        source1 = data.get('source1', '')
        source2 = data.get('source2', '')
        unified_diff = data.get('unified_diff', '')
        for tool in ['procyon', 'javap']:
            if tool in source1 or tool in source2:
                key = f"{group_id}:{artifact_id}:{version}"
                if key not in count_of_tools[tool]:
                    count_of_tools[tool][key] = {'diffs': set(), 'file': str(diffoscope_file)}
                count_of_tools[tool][key]['diffs'].add(unified_diff)

if __name__ == "__main__":
    for root, dirs, files in os.walk("results"):
        for file in files:
            if file.endswith(".diffoscope.json"):
                analyze_diffoscope(os.path.join(root, file))

    # Create a CSV file for releases with differences
    with open('releases_with_diffs.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Tool', 'GroupId', 'ArtifactId', 'Version'])

        for tool in ['procyon', 'javap']:
            for release, info in count_of_tools[tool].items():
                if info['diffs']:
                    group_id, artifact_id, version = release.split(':')
                    csvwriter.writerow([tool, group_id, artifact_id, version])
    
    print("CSV file 'releases_with_diffs.csv' has been created.")
