import argparse
from dataclasses import dataclass
import glob
import os
import sys
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
                    print(f'{os.path.join(root, directory)}: {len(diffoscope_files)} != {expected_ko}')
                
                

    # with open('mapping.json', 'r') as f:
    #     mapping = json.load(f)
    
    # for buildspec in mapping:
    #     groupId = mapping[buildspec]['groupId']
    #     artifactId = mapping[buildspec]['artifactId']
    #     version = mapping[buildspec]['version']

    #     path_to_results = os.path.join(PATH, groupId, artifactId, version)
    #     if not os.path.exists(path_to_results):
    #         print(f"Path {path_to_results} does not exist")
    #         continue

    #     total_projects += 1

    #     buildcompare_candidate = glob.glob(os.path.join(PATH, groupId, artifactId, version, '*.buildcompare'))
    #     if len(buildcompare_candidate) == 0:
    #         print(f"Build failed for {os.path.join(PATH, groupId, artifactId, version)}")
    #         continue
        
    #     total_projects_without_build_failed += 1

    #     parent_buildspec = pathlib.Path(buildspec).parent
    #     actual_buildcompare_candidate = glob.glob(os.path.join(parent_buildspec, '*.buildcompare'))
    #     actual_buildcompare = None
    #     for actual_buildcompare_it in actual_buildcompare_candidate:
    #         if version in actual_buildcompare_it:
    #             actual_buildcompare = actual_buildcompare_it
    #             break
    #     else:
    #         print(f"Ground truth is not there")
    #         ground_truth_is_not_there += 1
    #         continue


    #     if len(buildcompare_candidate) != 1:
    #         print(f"Expected one buildcompare file, but found {len(buildcompare_candidate)}, {os.path.join(PATH, groupId, artifactId, version)}")
    #         sys.exit(1)
    #     expected_buildcompare = buildcompare_candidate[0]
        
    #     print(f"Comparing {expected_buildcompare} with {actual_buildcompare}")
    #     if main(expected_buildcompare, actual_buildcompare):
    #         reproducible_project_count += 1
    #     else:
    #         unreproducible_project_count += 1

    # print(f"Total projects: {total_projects}")
    # print(f"Total projects without build failed: {total_projects_without_build_failed}")
    # print(f"Reproducible projects: {reproducible_project_count}")
    # print(f"Unreproducible projects: {unreproducible_project_count}")
    # print(f"Ground truth is not there: {ground_truth_is_not_there}")
    


