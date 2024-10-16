#!/usr/bin/env python3

from pathlib import Path
import os
import json
import sys
import argparse
import shutil

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

def format_readme(tool, data):
    readme = f"# {tool.capitalize()} Differences\n\n"
    for release, info in data.items():
        readme += f"## {release}\n\n"
        json_filename = f"{release.replace(':', '_')}.diffoscope.json"
        readme += f"Diffoscope JSON file: [{json_filename}]({json_filename})\n\n"
        for diff in info['diffs']:
            readme += f"```diff\n{diff}\n```\n\n"
    return readme

if __name__ == "__main__":
    for root, dirs, files in os.walk("results"):
        for file in files:
            if file.endswith(".diffoscope.json"):
                analyze_diffoscope(os.path.join(root, file))

    # Create docs directory if it doesn't exist
    os.makedirs("docs", exist_ok=True)

    # Create README files for each tool and copy JSON files
    for tool in ['procyon', 'javap']:
        readme_content = format_readme(tool, count_of_tools[tool])
        with open(f"docs/{tool}_README.md", 'w') as f:
            f.write(readme_content)
        
        # Copy and rename JSON files
        for release, release_info in count_of_tools[tool].items():
            json_file = release_info['file']
            new_json_filename = f"{release.replace(':', '_')}.diffoscope.json"
            shutil.copy2(json_file, os.path.join("docs", new_json_filename))

    print(f"README files and JSON files have been created/copied in the 'docs' directory.")
    
    results = {'procyon': {}, 'javap': {}}
    for key in count_of_tools:
        results[key]['releases'] = len(count_of_tools[key])
        results[key]['diffs'] = sum(len(info['diffs']) for info in count_of_tools[key].values())
    
    print("Summary of results:")
    print(json.dumps(results, indent=2))
