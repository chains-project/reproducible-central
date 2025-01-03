#!/usr/bin/env python3

from pathlib import Path
import os
import json
import sys
import argparse
import shutil

PROCYON_TOOL = "procyon -ec"
JAVAP_TOOL = "javap -verbose"

def parse_args():
    parser = argparse.ArgumentParser(description='Process release consistency')
    parser.add_argument('--base-dir', 
                       default="results",
                       help='Base directory for processing (default: results)')
    return parser.parse_args()

def analyze_diffoscope(diffoscope_file):
    with open(diffoscope_file, 'r') as file:
        data = file.read()

    if PROCYON_TOOL in data or JAVAP_TOOL in data:
        print(diffoscope_file)

if __name__ == "__main__":
    args = parse_args()
    base_dir = args.base_dir
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".diffoscope.json"):
                analyze_diffoscope(os.path.join(root, file))
