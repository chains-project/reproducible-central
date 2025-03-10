import os
import argparse
import glob
import json
import requests

MAVEN_CENTRAL_URL = "https://repo.maven.apache.org/maven2/"

def parse_args():
    parser = argparse.ArgumentParser(description='Process release consistency')
    parser.add_argument('--base-dir', 
                       default="results",
                       help='Base directory for processing (default: release-counter)')
    return parser.parse_args()

def load_success_builds():
    path_to_file = os.path.join('diffoscope-failures', "success_after_excluding_f_should_be_respected.txt")
    with open(path_to_file, 'r') as f:
        return set([line.strip() for line in f.readlines()])

def get_GAV(path_to_output):
    _, group_id, artifact_id, version = path_to_output.split(os.path.sep)
    return f"{group_id}:{artifact_id}:{version}"

def main():
    number_of_releases = 0
    args = parse_args()
    base_level = len(args.base_dir.split(os.path.sep))
    success_builds = load_success_builds()
    for root, dirs, files in os.walk(args.base_dir):
        for directory in dirs:
            current_level = len(root.split(os.path.sep))
            if current_level - base_level == 2:
                gav = get_GAV(os.path.join(root, directory))
                if gav in success_builds:
                    modules = os.path.join(root, directory, "output.txt")
                    with open(modules, 'r') as f:
                        releases = [line.strip() for line in f.readlines()]
                        
                        for release in releases:
                            g,a,v = release.split(":")
                            gav = requests.get(MAVEN_CENTRAL_URL + g.replace(".", "/") + "/" + a + "/" + v + "/")
                            if gav.status_code == 200:
                                number_of_releases += 1
                            else:
                                print(f"Release {g}:{a}:{v} not found in Maven Central")
    
    print(f"Total number of modules: {number_of_releases}")

if __name__ == "__main__":
    main()