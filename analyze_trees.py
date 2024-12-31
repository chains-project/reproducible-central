#!/usr/bin/env python3

from pathlib import Path
import os
import json
import sys
import argparse
import shutil

PROCYON_TOOL = "procyon -ec"
JAVAP_TOOL = "javap -verbose"

def analyze_diffoscope(diffoscope_file):
    with open(diffoscope_file, 'r') as file:
        data = file.read()

    if PROCYON_TOOL in data or JAVAP_TOOL in data:
        print(diffoscope_file)

if __name__ == "__main__":
    for root, dirs, files in os.walk("trees"):
        for file in files:
            analyze_diffoscope(os.path.join(root, file))
