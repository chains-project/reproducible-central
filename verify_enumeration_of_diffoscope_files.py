import argparse
from dataclasses import dataclass
import glob
import os
import sys
import re
import json
import pathlib
from typing import List


@dataclass
class BuildCompare:
    ok: int
    ko: int
    ok_files: List[str]
    ko_files: List[str]

def parse_args():
    parser = argparse.ArgumentParser(description='Process release consistency')
    parser.add_argument('--base-dir', 
                       default="results",
                       help='Base directory for processing (default: results)')
    return parser.parse_args()

def parse_buildcompare(buildcompare) -> BuildCompare:
    with open(buildcompare, 'r') as f:
        buildcompare_content = f.read()
    
    lines = buildcompare_content.split("\n")
    values = {}
    for line in lines:
        if "=" in line:
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip().strip('"')

    try:
        ok = int(values['ok'])
        ko = int(values['ko'])
        ok_files = sorted(values['okFiles'].split(" "))
        ko_files = sorted(values['koFiles'].split(" "))
    except KeyError as e:
        print(f"Missing values in {buildcompare}: {e}")
        sys.exit(1)

    return BuildCompare(ok, ko, ok_files, ko_files) 

def main(expected_buildcompare, actual_buildcompare):
    return parse_buildcompare(expected_buildcompare) == parse_buildcompare(actual_buildcompare)


if __name__ == '__main__':
    args = parse_args()
    PATH = args.base_dir

    depth = 3

    success_count = 0
    failure_count = 0
    _f = []
    file_not_there = []
    for root, dirs, files in os.walk(PATH):
        for directory in dirs:
            if os.path.join(root, directory).count(os.sep) == depth:
                # print(os.path.join(root, directory))
                buildcompare_candidate = glob.glob(os.path.join(root, directory, '*.buildcompare'))
                if len(buildcompare_candidate) == 0:
                    # print(f"Build failed for {os.path.join(root, directory)}")
                    continue

                if len(buildcompare_candidate) > 1:
                    print(f"Expected one buildcompare file, but found {len(buildcompare_candidate)}, {os.path.join(root, directory)}")
                    sys.exit(1)
                
                buildcompare = parse_buildcompare(buildcompare_candidate[0])
                expected_ko = buildcompare.ko

                oss_rebuild_files = glob.glob(os.path.join(root, directory, 'oss-rebuild', '*.json'))

                if len(oss_rebuild_files) <= 0:
                    continue

                if expected_ko == len(oss_rebuild_files):
                    success_count += 1
                
                else:
                    print(set(buildcompare.ko_files) - set([i.split('/')[5].replace('.json', '') for i in oss_rebuild_files]))
                    print(f"Expected {expected_ko} but found {len(oss_rebuild_files)} for {os.path.join(root, directory)}")
                    failure_count += 1
    
    print(f"Success count: {success_count}")
    print(f"Failure count: {failure_count}")

