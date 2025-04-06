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

diffoscope_files_with_all = 'diffoscope_files_with_all.txt'
with open(diffoscope_files_with_all, 'r') as f:
    diffoscope_files_with_all = [i.strip().split("/")[4].replace('.diffoscope.json', '') for i in f.readlines()]


args = parse_args()
base_dir = args.base_dir

SUCCESSFUL_NORMALIZATION = 0
FAILED_NORMALIZATION = 0
ERROR_IN_NORMALIZATION = 0

result = {
    "successful_normalization": {},
    "failed_normalization": {},
    "error_in_normalization": {}
}
for root, dirs, files in os.walk(base_dir):
    for directory in dirs:
        if directory == 'oss-rebuild-improved-2':
            jnorm_files = glob.glob(os.path.join(root, directory, '*.json'))
            for jnorm_file in jnorm_files:
                with open(jnorm_file, 'r') as f:
                    jnorm = json.load(f)
                    reference_exit_code = jnorm['reference']
                    rebuild_exit_code = jnorm['rebuild']
                    diff_exit_code = jnorm['diff']
                    
                    if ''.join(jnorm_file.split("/")[5].rsplit('.json', 1)) not in diffoscope_files_with_all:
                        continue

                    file_name = ''.join(jnorm_file.split("/")[5].rsplit('.json', 1))
                    diffoscope_path = pathlib.Path(jnorm_file).parent.parent

                    diffoscope_file_path = os.path.join(diffoscope_path, f"{file_name}.diffoscope.json")

                    g,a,v = diffoscope_file_path.split("/")[1:4]

                    diff_files = {
                        "diffoscope_diff": diffoscope_file_path,
                        "oss_rebuild_improved_2_diff": jnorm_file.replace('.json', '.diff')
                    }

                    if reference_exit_code == 0 and rebuild_exit_code == 0 and diff_exit_code == 0:
                        SUCCESSFUL_NORMALIZATION += 1
                        if f'{g}:{a}:{v}' in result["successful_normalization"]:
                            result["successful_normalization"][f'{g}:{a}:{v}'].append(diff_files)
                        else:
                            result["successful_normalization"][f'{g}:{a}:{v}'] = [diff_files]
                    elif reference_exit_code == 0 and rebuild_exit_code == 0 and diff_exit_code != 0:
                        FAILED_NORMALIZATION += 1
                        if f'{g}:{a}:{v}' in result["failed_normalization"]:
                            result["failed_normalization"][f'{g}:{a}:{v}'].append(diff_files)
                        else:
                            result["failed_normalization"][f'{g}:{a}:{v}'] = [diff_files]
                    else:
                        ERROR_IN_NORMALIZATION += 1
                        if f'{g}:{a}:{v}' in result["error_in_normalization"]:
                            result["error_in_normalization"][f'{g}:{a}:{v}'].append(diff_files)
                        else:
                            result["error_in_normalization"][f'{g}:{a}:{v}'] = [diff_files]

# Exclude these as they don't have javap or procyon
print(f"Successful normalization: {SUCCESSFUL_NORMALIZATION}")
print(f"Failed normalization: {FAILED_NORMALIZATION}")
print(f"Error in normalization: {ERROR_IN_NORMALIZATION}")

with open('oss_rebuild_improved_2_result.json', 'w+') as f:
    json.dump(result, f, indent=4)

            