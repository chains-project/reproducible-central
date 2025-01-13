from collections import defaultdict
import os
import argparse
import json
BASE_DIR = 'trees'

PROCYON_TOOL = "procyon -ec"
JAVAP_TOOL = "javap -verbose"

def parse_args():
    parser = argparse.ArgumentParser(description='Process release consistency')
    parser.add_argument('--base-dir', 
                       default="results",
                       help='Base directory for processing (default: results)')
    return parser.parse_args()

def minify_diffoscope(diffoscope_file_path, diffoscope_filename, base_dir, tree_g, tree_a, tree_v):
    diffoscope_file_tree = os.path.join('trees', f'{tree_g}/{tree_a}/{tree_v}/{diffoscope_filename}.txt')
    with open(diffoscope_file_tree, 'r') as file:
        sources = get_and_sanitize_leaf_nodes(file.readlines())

    # huge files cannot be read
    if os.path.getsize(diffoscope_file_path) > 1000000000:
        return

    if len(sources) == 0:
        return
    
    minified_diffoscope_dir = os.path.join(f'minified_{base_dir}', f'{tree_g}/{tree_a}/{tree_v}')
    os.makedirs(minified_diffoscope_dir, exist_ok=True)

    # we don't iterate by idx because we know if the source is same under the same tool, it will most likely be the same
    for source in sources:
        minified_diffoscope_file = os.path.join(minified_diffoscope_dir, f'{source.replace("/", "_")}.diffoscope.json')
        minify(source, diffoscope_file_path, minified_diffoscope_file)

def minify(source, diffoscope_file_path, minified_diffoscope_file):
    with open(minified_diffoscope_file, 'w') as file:
        file.write(json.dumps(get_diffoscope_for_source(diffoscope_file_path, source), indent=2))

def get_diffoscope_for_source(diffoscope_file_path, source):
    with open(diffoscope_file_path, 'r') as file:
        data = json.load(file)
            
    return process_data(data, source)

def process_data(data, source):
    if data.get('source1') == source:
        return data
    if data.get('source2') == source:
        return data
    
    if 'details' in data:
        for detail in data['details']:
            result = process_data(detail, source)
            if result is not None:
                return result
    return None

def get_and_sanitize_leaf_nodes(all_lines):
    leaf_nodes = all_lines[-1]

    result = []
    for source in leaf_nodes.split(','):
        if 'zipinfo' in source or 'zipdetails' in source or 'zipnote' in source:
            result.append(source.strip())
        else:
            # if it is any thing other than the above, we return empty list
            return []
    return result


if __name__ == "__main__":
    args = parse_args()
    base_dir = args.base_dir
    os.makedirs(f'minified_{base_dir}', exist_ok=True)
    # Walk through results directory

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

                minify_diffoscope(path_to_diffoscope_file, file_name, base_dir, group_id, artifact_id, version)
