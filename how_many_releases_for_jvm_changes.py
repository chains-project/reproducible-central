import json
import os
import argparse

PROCYON_TOOL = "procyon -ec"
JAVAP_TOOL = "javap -verbose"



def list_of_diffoscope_files_with_jvm_changes():
    with open('diffoscope_files_with_jvm.txt', 'r') as f:
        diffoscope_files = [i.strip().split("/")[-1] for i in f.readlines()]
    
    return diffoscope_files

def main():
    maven_projects_with_only_jvm = []

    diffoscope_files = list_of_diffoscope_files_with_jvm_changes()
    with open("unreproducible_maven_projects_to_releases.json", "r") as f:
        maven_projects = json.load(f)
    
    for project in maven_projects:
        project_name = project["name"]
        maven_releases = project["maven_releases"]
        maven_releases_with_jvm_changes = []
        for release in maven_releases:
            unreproducible_artifacts = release["unreproducible_artifacts"]
            for artifact in unreproducible_artifacts:
                if artifact in diffoscope_files:
                    existing_entry = next((r for r in maven_releases_with_jvm_changes if release["gav"] == r["gav"]), None)
                    if existing_entry:
                        existing_entry["unreproducible_artifacts"].append(artifact)
                    else:
                        maven_releases_with_jvm_changes.append({
                            "gav": release["gav"],
                            "unreproducible_artifacts": [artifact]
                        })
        if len(maven_releases_with_jvm_changes) > 0:
            maven_projects_with_only_jvm.append({
                "name": project_name,
                "maven_releases": maven_releases_with_jvm_changes,
            })
    json.dump(maven_projects_with_only_jvm, open("maven_projects_with_jvm_changes.json", "w"), indent=2)


if __name__ == "__main__":
    main()

