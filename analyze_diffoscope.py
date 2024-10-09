#!/usr/bin/env python3

from pathlib import Path
import os
import json
import sys
import requests
from github import Github

count_of_tools = {'procyon': {}, 'javap': {}}

def process_details(details, group_id, artifact_id, count_of_tools, version, diffoscope_file):
    for detail in details:
        source1 = detail.get('source1', '')
        source2 = detail.get('source2', '')
        unified_diff = detail.get('unified_diff', '')

        if 'procyon' in source1 or 'procyon' in source2:
            if f"{group_id}:{artifact_id}:{version}" not in count_of_tools['procyon']:
                count_of_tools['procyon'][f"{group_id}:{artifact_id}:{version}"] = set()
            count_of_tools['procyon'][f"{group_id}:{artifact_id}:{version}"].add(unified_diff)
        if 'javap' in source1 or 'javap' in source2:
            if f"{group_id}:{artifact_id}:{version}" not in count_of_tools['javap']:
                count_of_tools['javap'][f"{group_id}:{artifact_id}:{version}"] = set()
            count_of_tools['javap'][f"{group_id}:{artifact_id}:{version}"].add(unified_diff)
        
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
        unified_diff = data.get('unified_diff', '')
        if 'procyon' in source1 or 'procyon' in source2:
            if f"{group_id}:{artifact_id}:{version}" not in count_of_tools['procyon']:
                count_of_tools['procyon'][f"{group_id}:{artifact_id}:{version}"] = set()
            count_of_tools['procyon'][f"{group_id}:{artifact_id}:{version}"].add(unified_diff)
        if 'javap' in source1 or 'javap' in source2:
            if f"{group_id}:{artifact_id}:{version}" not in count_of_tools['javap']:
                count_of_tools['javap'][f"{group_id}:{artifact_id}:{version}"] = set()
            count_of_tools['javap'][f"{group_id}:{artifact_id}:{version}"].add(unified_diff)

def create_github_comment(repo, issue_number, comment_body, dry_run=False):
    if dry_run:
        print(f"Dry run: Comment for issue #{issue_number}")
        print("---Comment content start---")
        print(comment_body)
        print("---Comment content end---")
        print()
        return

    # GitHub API endpoint
    url = f"https://api.github.com/repos/{repo}/issues/{issue_number}/comments"
    
    # GitHub personal access token
    token = os.getenv('GITHUB_TOKEN')
    
    # Headers for authentication
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json"
    }
    
    # Create the comment
    response = requests.post(url, json={"body": comment_body}, headers=headers)
    
    if response.status_code == 201:
        print(f"Comment created successfully for issue #{issue_number}")
    else:
        print(f"Failed to create comment. Status code: {response.status_code}")
        print(f"Response: {response.text}")

def format_comment(tool, elements):
    comment = f"### {tool}\n\n"
    for el in elements:
        comment += f"```diff\n{el}\n```\n\n"
    return comment



if __name__ == "__main__":
    for root, dirs, files in os.walk("results"):
        for file in files:
            if file.endswith(".diffoscope.json"):
                analyze_diffoscope(os.path.join(root, file))

    repo = "algomaster99/reproducible-central"

    for key in count_of_tools:
        if key == 'procyon':
            issue_number = 4
        elif key == 'javap':
            issue_number = 5
        for tool in count_of_tools[key]:
            elements = count_of_tools[key][tool]
            comment_body = format_comment(tool, elements)
            create_github_comment(repo, issue_number, comment_body, dry_run=True)
    print("All comments have been posted to the GitHub issue.")
    
