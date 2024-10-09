import os

RESULTS_DIR = "results"

releases_with_diffoscope = set()

for root, dirs, files in os.walk(RESULTS_DIR):
    for file in files:
        if file.endswith(".diffoscope.json"):
            releases_with_diffoscope.add(root)

print(f"Releases with diffoscope: {releases_with_diffoscope}")
print(f"Total releases: {len(releases_with_diffoscope)}")
