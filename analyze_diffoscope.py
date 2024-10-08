#!/usr/bin/env python3

from pathlib import Path
import os
import json
import sys

count_of_tools = {'procyon': {}, 'javap': {}}

def print_count_of_tools():
    for key in count_of_tools:
        print(f"## {key}")
        for tool in count_of_tools[key]:
            print(f"### {tool}")
            for diffoscope_file in count_of_tools[key][tool]:
                print(f"- {diffoscope_file}")

def process_details(details, group_id, artifact_id, count_of_tools, version, diffoscope_file):
    for detail in details:
        source1 = detail.get('source1', '')
        source2 = detail.get('source2', '')

        if 'procyon' in source1 or 'procyon' in source2:
            if f"{group_id}:{artifact_id}:{version}" not in count_of_tools['procyon']:
                count_of_tools['procyon'][f"{group_id}:{artifact_id}:{version}"] = set()
            count_of_tools['procyon'][f"{group_id}:{artifact_id}:{version}"].add(diffoscope_file)
        if 'javap' in source1 or 'javap' in source2:
            if f"{group_id}:{artifact_id}:{version}" not in count_of_tools['javap']:
                count_of_tools['javap'][f"{group_id}:{artifact_id}:{version}"] = set()
            count_of_tools['javap'][f"{group_id}:{artifact_id}:{version}"].add(diffoscope_file)
        
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
        details = data['details']
        process_details(details, group_id, artifact_id, count_of_tools, version, diffoscope_file)
    else:
        source1 = data.get('source1', '')
        source2 = data.get('source2', '')
        if 'procyon' in source1 or 'procyon' in source2:
            if f"{group_id}:{artifact_id}:{version}" not in count_of_tools['procyon']:
                count_of_tools['procyon'][f"{group_id}:{artifact_id}:{version}"] = set()
            count_of_tools['procyon'][f"{group_id}:{artifact_id}:{version}"].add(diffoscope_file)
        if 'javap' in source1 or 'javap' in source2:
            if f"{group_id}:{artifact_id}:{version}" not in count_of_tools['javap']:
                count_of_tools['javap'][f"{group_id}:{artifact_id}:{version}"] = set()
            count_of_tools['javap'][f"{group_id}:{artifact_id}:{version}"].add(diffoscope_file)

if __name__ == "__main__":
    for root, dirs, files in os.walk("results"):
        for file in files:
            if file.endswith(".diffoscope.json"):
                analyze_diffoscope(os.path.join(root, file))

    print_count_of_tools()
