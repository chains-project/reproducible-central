import os
import argparse
import json

def parse_args():
    parser = argparse.ArgumentParser(description='Process release consistency')
    parser.add_argument('--base-dir', 
                       default="results",
                       help='Base directory for processing (default: release-counter)')
    return parser.parse_args()

PROCYON_TOOL = "procyon -ec"
JAVAP_TOOL = "javap -verbose"

args = parse_args()

with open('java/unreproducible_maven_projects_to_releases.json', 'r') as f:
    unreproducible_maven_projects_to_releases = json.load(f)

list_of_artifacts_with_jvm_changes = []
total_artifacts = 0
all_artifacts = 0
for project in unreproducible_maven_projects_to_releases:
    g,a,v = project['name'].split(":")

    for release in project['maven_releases']:
        if 'comment' in release:
            continue

        total_artifacts += len(release['unreproducibleArtifacts'])
        all_artifacts += len(release['allArtifacts'])
        for uA in release['unreproducibleArtifacts']:
            path_to_diffoscope_file = os.path.join(args.base_dir, g, a, v, uA)
        
            with open(path_to_diffoscope_file, 'r') as f:
                data = f.read()
                if PROCYON_TOOL in data or JAVAP_TOOL in data:
                    list_of_artifacts_with_jvm_changes.append(path_to_diffoscope_file)

with open('diffoscope_files_with_jvm.txt', 'w+') as f:
    f.writelines([f"{line}\n" for line in sorted(list_of_artifacts_with_jvm_changes)])

print(f"Total number of unreproducible artifacts: {total_artifacts}")
print(f"Number of artifacts in all releases: {all_artifacts}")

