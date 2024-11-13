#!/usr/bin/env python3

from pathlib import Path
import os
import json
import sys
import argparse
import shutil

count_of_tools = {'procyon': {}, 'javap': {}}
artifact_name = ""

def process_details(details, group_id, artifact_id, count_of_tools, version, diffoscope_file):
    for detail in details:
        source1 = detail.get('source1', '')
        source2 = detail.get('source2', '')
        candidate = get_artifact_name_or_none(source1)
        if candidate:
            artifact_name = candidate

        for tool in ['procyon', 'javap']:
            if tool in source1 or tool in source2:
                key = f"{group_id}:{artifact_id}:{version}"
                if key not in count_of_tools[tool]:
                    count_of_tools[tool][key] = set([artifact_name])
                else:
                    count_of_tools[tool][key].add(artifact_name)
        
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
        candidate = get_artifact_name_or_none(source1)
        if candidate:
            artifact_name = candidate
        for tool in ['procyon', 'javap']:
            if tool in source1 or tool in source2:
                key = f"{group_id}:{artifact_id}:{version}"
                if key not in count_of_tools[tool]:
                    count_of_tools[tool][key] = set([artifact_name])
                else:
                    count_of_tools[tool][key].add(artifact_name)

def get_artifact_name_or_none(source):
    if source.endswith(".jar") or source.endswith(".zip"):
        return source.split("/")[-1]
    
    return None

if __name__ == "__main__":
    for root, dirs, files in os.walk("results"):
        for file in files:
            if file.endswith(".diffoscope.json"):
                analyze_diffoscope(os.path.join(root, file))

    print(count_of_tools)

