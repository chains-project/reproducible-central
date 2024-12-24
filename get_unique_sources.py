#!/usr/bin/env python3

from pathlib import Path
import os
import json
from collections import defaultdict
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description='Process release consistency')
    parser.add_argument('--base-dir', 
                       default="results",
                       help='Base directory for processing (default: results)')
    return parser.parse_args()

def get_unique_sources(diffoscope_file):
    sources = defaultdict(int)
    with open(diffoscope_file, 'r') as file:
        data = json.load(file)
    
    # Process nested details recursively
    def process_details(details):
        for detail in details:
            if 'details' in detail:
                process_details(detail['details'])
            else:
                if 'source1' in detail:
                    sources[detail['source1']] += 1
                if 'source2' in detail:
                    sources[detail['source2']] += 1

    
    if 'details' in data:
        process_details(data['details'])
    
    return sources

if __name__ == "__main__":
    args = parse_args()
    base_dir = args.base_dir
    all_sources = defaultdict(int)
    
    # Walk through results directory
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".diffoscope.json"):
                file_sources = get_unique_sources(os.path.join(root, file))
                for source, count in file_sources.items():
                    all_sources[source] += count
    
    # Write results to file
    with open("unique_sources_with_frequency.txt", "w") as file:
        for source, count in sorted(all_sources.items()):
            file.write(f"{source}: {count}\n") 