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

def minify_diffoscope(diffoscope_root, diffoscope_filename, base_dir):
    _, group_id, artifact_id, version = diffoscope_root.split('/')
    diffoscope_file_tree = os.path.join('trees', f'{group_id}/{artifact_id}/{version}/{diffoscope_filename}.txt')
    with open(diffoscope_file_tree, 'r') as file:
        sources = get_and_sanitize_leaf_nodes(file.readlines())

    if len(sources) == 0:
        return
    
    minified_diffoscope_dir = os.path.join(f'minified_{base_dir}', f'{group_id}/{artifact_id}/{version}')
    os.makedirs(minified_diffoscope_dir, exist_ok=True)

    # we don't iterate by idx because we know if the source is same under the same tool, it will most likely be the same
    for source in sources:
        minified_diffoscope_file = os.path.join(minified_diffoscope_dir, f'{source.replace("/", "_")}.diffoscope.json')
        minify(source, os.path.join(diffoscope_root, diffoscope_filename), minified_diffoscope_file)

def minify(source, diffoscope_file, minified_diffoscope_file):
    with open(minified_diffoscope_file, 'w') as file:
        file.write(json.dumps(get_diffoscope_for_source(diffoscope_file, source), indent=2).replace('\\n', '\n'))

def get_diffoscope_for_source(diffoscope_file, source):
    with open(diffoscope_file, 'r') as file:
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
        if 'zipinfo' in source:
            continue
        if 'zipdetails' in source:
            continue
        if 'zipnote' in source:
            continue
        # we want to skip these tools because they require much deeper analysis
        if PROCYON_TOOL in source or JAVAP_TOOL in source:
            continue
        result.append(source.strip())
    return result


if __name__ == "__main__":
    args = parse_args()
    base_dir = args.base_dir
    os.makedirs(f'minified_{base_dir}', exist_ok=True)
    # Walk through results directory
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".diffoscope.json"):
                minify_diffoscope(root, file, base_dir)
