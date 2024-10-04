#!/usr/bin/env python3

import os
import json
import sys

count_of_tools = {}

def analyze_diffoscope(diffoscope_file):
    with open(diffoscope_file, 'r') as file:
        data = json.load(file)

    # Extract relevant information from the diffoscope data
    details = data['details']
    for detail in details:
        source1 = detail['source1']
        source2 = detail['source2']
        print(source1, source2)
        if source1 != source2:
            print(f"source1 and source2 are probably files names.")
            count_of_tools['unix_diff'] = count_of_tools.get('unix_diff', 0) + 1
        else:
            count_of_tools[source1] = count_of_tools.get(source1, 0) + 1

if __name__ == "__main__":
    for root, dirs, files in os.walk("results"):
        for file in files:
            if file.endswith(".diffoscope.json"):
                analyze_diffoscope(os.path.join(root, file))

    print(count_of_tools)
