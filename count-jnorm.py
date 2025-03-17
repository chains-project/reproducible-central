import os
import argparse
import glob
import pathlib
import json

def parse_args():
    parser = argparse.ArgumentParser(description='Process release consistency')
    parser.add_argument('--base-dir', 
                       default="results",
                       help='Base directory for processing (default: release-counter)')
    return parser.parse_args()

diffoscope_files_with_jvm = 'diffoscope_files_with_jvm.txt'
with open(diffoscope_files_with_jvm, 'r') as f:
    diffoscope_files_with_jvm = [i.strip().split("/")[4].replace('.diffoscope.json', '') for i in f.readlines()]


args = parse_args()
base_dir = args.base_dir

SOURCES = 0
SUCCESSFUL_NORMALIZATION = 0
FAILED_NORMALIZATION = 0
ERROR_IN_NORMALIZATION = 0

result = {
    "successful_normalization": set(),
    "failed_normalization": set(),
    "error_in_normalization": set()
}
for root, dirs, files in os.walk(base_dir):
    for directory in dirs:
        if directory == 'jnorm':
            jnorm_files = glob.glob(os.path.join(root, directory, '*.json'))
            for jnorm_file in jnorm_files:
                with open(jnorm_file, 'r') as f:
                    jnorm = json.load(f)
                    reference_exit_code = jnorm['reference']
                    rebuild_exit_code = jnorm['rebuild']
                    diff_exit_code = jnorm['diff']
                    
                    if jnorm_file.split("/")[5].replace('.json', '') not in diffoscope_files_with_jvm:
                        continue

                    file_name = jnorm_file.split("/")[5].replace('.json', '')
                    diffoscope_path = pathlib.Path(jnorm_file).parent.parent

                    diffoscope_file_path = os.path.join(diffoscope_path, f"{file_name}.diffoscope.json")

                    if reference_exit_code == 0 and rebuild_exit_code == 0 and diff_exit_code == 0:
                        if '-sources' in jnorm_file:
                            SOURCES += 1
                        else:
                            SUCCESSFUL_NORMALIZATION += 1
                            result["successful_normalization"].add(diffoscope_file_path)
                    elif reference_exit_code == 0 and rebuild_exit_code == 0 and diff_exit_code != 0:
                        FAILED_NORMALIZATION += 1
                        result["failed_normalization"].add(diffoscope_file_path)
                    else:
                        ERROR_IN_NORMALIZATION += 1
                        result["error_in_normalization"].add(diffoscope_file_path)

# Exclude these as they don't have javap or procyon
print(f"Sources: {SOURCES}")
print(f"Successful normalization: {SUCCESSFUL_NORMALIZATION}")
print(f"Failed normalization: {FAILED_NORMALIZATION}")
print(f"Error in normalization: {ERROR_IN_NORMALIZATION}")

with open('jnorm_result.json', 'w+') as f:
    result = {
        "successful_normalization": list(result["successful_normalization"]),
        "failed_normalization": list(result["failed_normalization"]),
        "error_in_normalization": list(result["error_in_normalization"])
    }
    json.dump(result, f, indent=4)

            