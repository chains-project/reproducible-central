#!/usr/bin/env python3

from pathlib import Path
import os
import json
import sys

count_of_tools = {'procyon': set(), 'javap': set()}

def process_details(details, group_id, artifact_id, count_of_tools, version):
    for detail in details:
        source1 = detail.get('source1', '')
        source2 = detail.get('source2', '')
        
        if 'procyon' in source1 or 'procyon' in source2:
            count_of_tools['procyon'].add(f"{group_id}:{artifact_id}:{version}")
        if 'javap' in source1 or 'javap' in source2:
            count_of_tools['javap'].add(f"{group_id}:{artifact_id}:{version}")
        
        # Recursively process nested details
        if 'details' in detail:
            process_details(detail['details'], group_id, artifact_id, count_of_tools, version)

def analyze_diffoscope(diffoscope_file):
    with open(diffoscope_file, 'r') as file:
        data = json.load(file)

    diffoscope_file = Path(diffoscope_file)
    version = diffoscope_file.parent.name
    artifact_id = diffoscope_file.parent.parent.name
    group_id = diffoscope_file.parent.parent.parent.name
    details = data['details']
    process_details(details, group_id, artifact_id, count_of_tools, version)

if __name__ == "__main__":
    for root, dirs, files in os.walk("results"):
        for file in files:
            if file.endswith(".diffoscope.json"):
                analyze_diffoscope(os.path.join(root, file))

    print(count_of_tools)
