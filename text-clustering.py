import argparse
import os
import queue
import json

all_diffoscope_files = []
all_sources = []

def parse_args():
    parser = argparse.ArgumentParser(description='Process release consistency')
    parser.add_argument('--base-dir', 
                       default="results",
                       help='Base directory for processing (default: results)')
    return parser.parse_args()

args = parse_args()

tree_dir = 'trees'
os.makedirs(tree_dir, exist_ok=True)

def create_level_order_traversal_for_diffoscope(data, file_name, group_id, artifact_id, version):
    os.makedirs(f'trees/{group_id}/{artifact_id}/{version}', exist_ok=True)
    with open(f'trees/{group_id}/{artifact_id}/{version}/{file_name}.txt', 'w') as f:
        q = queue.Queue()
        q.put(data)
        while not q.empty():
            size = q.qsize()
            sources = []
            for i in range(size):
                current = q.get()
                sources.append(current['source1'])
                if current.get('details'):
                    for detail in current['details']:
                        q.put(detail)
            f.write(",".join(sources) + "\n")


with open(os.path.join('diffoscope-failures', "all_success.txt"), 'r') as f:
    all_success = [i.strip() for i in f.readlines()]

with open('unreproducible_maven_projects_to_releases.json', 'r') as f:
    unreproducible_projects = json.load(f)

for project in unreproducible_projects:
    project_name = project['name']
    original_group_id, original_artifact_id, original_version = project_name.split(":")

    for release in project['maven_releases']:
        group_id, artifact_id, version = release['gav'].split(":")
        
        for unreproducible_artifact in release['unreproducible_artifacts']:
            file_name = unreproducible_artifact

            path_to_diffoscope_file = os.path.join(args.base_dir, original_group_id, original_artifact_id, original_version, file_name)
            with open(path_to_diffoscope_file, 'r') as f:
                data = json.load(f)

            create_level_order_traversal_for_diffoscope(data, file_name, group_id, artifact_id, version)

