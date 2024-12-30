import tlsh
from collections import defaultdict
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


for root, dirs, files in os.walk(args.base_dir):
    for file in files:
        last_two_sources = []
        if file.endswith(".diffoscope.json"):
            _, group_id, artifact_id, version = root.split('/')

            with open(os.path.join(root, file), 'r') as f:
                data = json.load(f)
            

            create_level_order_traversal_for_diffoscope(data, file, group_id, artifact_id, version)
