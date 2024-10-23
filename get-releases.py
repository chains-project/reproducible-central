#!/usr/bin/env python3

from pathlib import Path
import os
import json
import csv

projects = set()
def analyze_diffoscope(diffoscope_file):
    with open(diffoscope_file, 'r') as file:
        data = json.load(file)

    diffoscope_file = Path(diffoscope_file)
    version = diffoscope_file.parent.name
    artifact_id = diffoscope_file.parent.parent.name
    group_id = diffoscope_file.parent.parent.parent.name
    
    javap_string = "javap -verbose -constants -s -l -private {}"
    procyon_string = "procyon -ec {}"

    if javap_string in data or procyon_string in data:
        projects.add(f"{group_id}:{artifact_id}:{version}")

if __name__ == "__main__":
    for root, dirs, files in os.walk("results"):
        for file in files:
            if file.endswith(".diffoscope.json"):
                analyze_diffoscope(os.path.join(root, file))

    
    for project in projects:
        print(project)
    print(f"Found {len(projects)} projects with differences")