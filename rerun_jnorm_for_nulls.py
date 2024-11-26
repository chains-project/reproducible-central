import json
import os
import subprocess
from pathlib import Path

def run_jnorm_command(version_dir, artifact_path, dirname_in_jnorm, build):
    cmd = [
        "docker", "run",
        "--user", str(os.getuid()),
        "--rm",
        "-v", f"{version_dir}:/output",
        "algomaster99/jnorm",
        "-o", "-n", "-s", "-a", "-p",
        "-i", f"/output/{artifact_path}",
        "-d", f"/output/jNorm/{dirname_in_jnorm}/{build}/"
    ]
    
    print(f"Running command: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, check=False, capture_output=True, text=True)
        print(f"Exit code: {result.returncode}")
        with open(os.path.join(version_dir, 'jNorm', dirname_in_jnorm, f"{build}.log"), 'w') as f:
            f.write(result.stdout)
            f.write(result.stderr)
        print("stdout:", result.stdout)
        print("stderr:", result.stderr)
        return result.returncode
    except Exception as e:
        print(f"Error running command: {e}")
        return -1

def run_diff(reference_path, rebuild_path, diff_file):
    cmd = [
        'diff', '-u', reference_path, rebuild_path,
    ]
    print(f"Running command: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, check=False, capture_output=True, text=True)
        print(f"Exit code: {result.returncode}")
        with open(diff_file, 'w') as f:
            f.write(result.stdout)
            f.write(result.stderr)
        print("stdout:", result.stdout)
        print("stderr:", result.stderr)
        return result.returncode
    except Exception as e:
        print(f"Error running command: {e}")
        return -1

def process_artifact(gav, artifact_info):
    group_id, artifact_id, version = gav.split(':')
    
    reference_path = artifact_info['reference']
    
    # Get the base path from reference path
    rebuild_path = reference_path.replace('reference', 'rebuild')
    
    if 'dependency-check-cli' in rebuild_path:
        rebuild_path = rebuild_path.replace('-cli', '')
    elif 'drill-hive-exec-shaded' in rebuild_path:
        rebuild_path = rebuild_path.replace('-jar', '')
    else:
        raise ValueError(f"Unknown jar name: {rebuild_path}")
        
    reference_path_for_docker = os.path.join(os.path.basename(os.path.dirname(reference_path)), os.path.basename(reference_path))
    rebuild_path_for_docker = os.path.join(os.path.basename(os.path.dirname(rebuild_path)), os.path.basename(rebuild_path))
    
    print(f"Rebuild path: {rebuild_path_for_docker}")

    version_dir = Path(rebuild_path).parent.parent
    
    rebuild_exit_code = run_jnorm_command(os.path.abspath(version_dir),
                        rebuild_path_for_docker,
                        os.path.basename(reference_path), 'rebuild')
    reference_exit_code = run_jnorm_command(os.path.abspath(version_dir),
                        reference_path_for_docker,
                        os.path.basename(reference_path), 'reference')

    diff_exit_code = run_diff(os.path.join(version_dir, 'jNorm', os.path.basename(reference_path), 'reference'),
                             os.path.join(version_dir, 'jNorm', os.path.basename(reference_path), 'rebuild'),
                             os.path.join(version_dir, 'jNorm', os.path.basename(reference_path), 'diff.diff'))

    jNorm_status = 0
    if reference_exit_code == 0 and rebuild_exit_code == 0 and diff_exit_code == 0:
        jNorm_status = 0
    elif reference_exit_code == 0 and rebuild_exit_code == 0 and diff_exit_code == 1:
        jNorm_status = 1
    else:
        jNorm_status = 2

        
    summary_path = os.path.join(version_dir, 'jNorm', 'jNorm_summary.json')
    if os.path.exists(summary_path):
        with open(summary_path, 'r') as f:
            summary = json.load(f)
        
        # Get the rebuild path from make-release-consistent-file-paths.json
        with open('make-release-consistent-file-paths.json', 'r') as f:
            file_paths = json.load(f)
            
        if gav in file_paths:
            for file_artifact in file_paths[gav]:
                print(f"file_artifact: {file_artifact}")
                print(f"reference_path: {reference_path}")
                if os.path.basename(file_artifact['reference']) == os.path.basename(reference_path):
                    file_artifact['rebuild'] = rebuild_path
                    break
        
        with open('make-release-consistent-file-paths.json', 'w') as f:
            json.dump(file_paths, f, indent=2)
        
        print("\nUpdating summary:")
        print("Before:")
        for artifact in summary['artifacts']:
            if artifact['artifact_name'] == os.path.basename(reference_path):
                print(json.dumps(artifact, indent=2))
                
                # Update the artifact with path from file_paths
                artifact['rebuild'] = os.path.basename(rebuild_path)
                artifact['jNorm'] = jNorm_status
                print("\nAfter:")
                print(json.dumps(artifact, indent=2))
        
        # Write the updated summary
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\nUpdated summary file: {summary_path}")

def main():
    # Read the file paths JSON
    with open('make-release-consistent-file-paths.json', 'r') as f:
        gav_map = json.load(f)
    
    # Process each GAV
    for gav, artifacts in gav_map.items():
        for artifact in artifacts:
            if artifact['rebuild'] is None:
                print(f"\nProcessing {gav} - {artifact['reference']}")
                process_artifact(gav, artifact)
                return

if __name__ == "__main__":
    main() 