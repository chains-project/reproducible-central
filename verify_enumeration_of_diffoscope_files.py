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

    total_projects = 0
    total_projects_without_build_failed = 0
    reproducible_project_count = 0
    unreproducible_project_count = 0
    ground_truth_is_not_there = 0

    depth = 3

    success_count = 0
    _f_count = 0
    file_not_there_count = 0
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

                diffoscope_files = glob.glob(os.path.join(root, directory, '*.diffoscope.json'))

                if len(diffoscope_files) != expected_ko:
                    buildspec = glob.glob(os.path.join(root, directory, '*.buildspec'))[0]
                    with open(buildspec, 'r') as f:
                        buildspec_content = f.read()
                    
                    regex = r"(?<=mvn).*-f.*(?=pom\.xml)"
                    regex = re.compile(regex)
                    if regex.search(buildspec_content):
                        print(f'{os.path.join(root, directory)}: -f should be respected')
                        _f_count += 1
                    else:
                        print(f'{os.path.join(root, directory)}: file not there in reference or rebuild')
                        file_not_there_count += 1
                else:
                    success_count += 1
    
    print(f"Success count: {success_count}")
    print(f"File not there count: {file_not_there_count}")
    print(f"_f count: {_f_count}")
