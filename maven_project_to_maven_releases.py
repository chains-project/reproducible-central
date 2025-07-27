import os
import argparse
import glob
import json
import re

def parse_args():
    parser = argparse.ArgumentParser(description='Process release consistency')
    parser.add_argument('--base-dir', 
                       default="release-counter",
                       help='Base directory for processing (default: release-counter)')
    return parser.parse_args()

def load_success_builds():
    path_to_file = os.path.join('diffoscope-failures', "success_after_excluding_f_should_be_respected.txt")
    with open(path_to_file, 'r') as f:
        return set([line.strip() for line in f.readlines()])

def get_GAV(path_to_output):
    _, group_id, artifact_id, version = path_to_output.split(os.path.sep)
    return f"{group_id}:{artifact_id}:{version}"

def extract_artifact_id(artifact_name, version):
    # Get the extension
            # Find where version starts
    if artifact_name.startswith("arice-tests-1.0.1"):
        return "arice-tests"
    if artifact_name.startswith("arice-tests-1.0.2"):
        return "arice-tests"
    if artifact_name.startswith("arice-tests-1.0.0"):
        return "arice-tests"
    if artifact_name.startswith("arice-tests-1.1.0"):
        return "arice-tests"
    if artifact_name.startswith("junit-platform-console-standalone"):
        version = re.sub(r'^5(?=\.\d+\.\d+)', '1', version)
    if artifact_name.startswith("junit-platform-reporting"):
        version = re.sub(r'^5(?=\.\d+\.\d+)', '1', version)
    if artifact_name.startswith("junit-platform-commons"):
        version = re.sub(r'^5(?=\.\d+\.\d+)', '1', version)
    if artifact_name.startswith("junit-platform-console"):
        version = re.sub(r'^5(?=\.\d+\.\d+)', '1', version)
    if artifact_name.startswith("junit-platform-suite-commons"):
        version = re.sub(r'^5(?=\.\d+\.\d+)', '1', version)
    if artifact_name.startswith("junit-platform-jfr"):
        version = re.sub(r'^5(?=\.\d+\.\d+)', '1', version)
    if artifact_name.startswith("junit-platform-testkit"):
        version = re.sub(r'^5(?=\.\d+\.\d+)', '1', version)
    if artifact_name.startswith("junit-platform-suite"):
        version = re.sub(r'^5(?=\.\d+\.\d+)', '1', version)
    if artifact_name.startswith("junit-platform-launcher"):
        version = re.sub(r'^5(?=\.\d+\.\d+)', '1', version)
    if artifact_name.startswith("junit-platform-engine"):
        version = re.sub(r'^5(?=\.\d+\.\d+)', '1', version)
    if artifact_name.startswith("junit-platform-runner"):
        version = re.sub(r'^5(?=\.\d+\.\d+)', '1', version)
    version_start = artifact_name.find(f"-{version}")
    if version_start != -1:
        # Keep everything before version, don't add extension
        return artifact_name[:version_start]
    
    return None

def get_matching_gav(artifact_id, maven_modules):
    artifact_id_from_module = maven_modules.get("artifactId")
    if maven_modules.get('groupId') == 'io.opentelemetry':
        return maven_modules.get('groupId'), artifact_id, maven_modules.get("version")
    
    if maven_modules.get('groupId') ==  'io.opentelemetry.instrumentation' and 'opentelemetry-javaagent-rmi' == artifact_id:
        return "io.opentelemetry.javaagent.instrumentation", artifact_id, maven_modules.get("version")
    if maven_modules.get('groupId') ==  'io.opentelemetry.instrumentation' and 'opentelemetry-javaagent' == artifact_id:
        return "io.opentelemetry.javaagent", artifact_id, maven_modules.get("version").replace('-alpha', '')
    if maven_modules.get('groupId') ==  'io.opentelemetry.instrumentation':
        return maven_modules.get('groupId'), artifact_id, maven_modules.get("version")
    if maven_modules.get('groupId') == 'org.mockito':
        if artifact_id_from_module == 'mockito':
            artifact_id_from_module = 'mockito-core'
        else:
            artifact_id_from_module = f"{maven_modules.get('groupId').replace('org.','')}-{artifact_id_from_module}"
    if artifact_id_from_module == artifact_id:
        return maven_modules.get('groupId'), artifact_id_from_module, maven_modules.get('version')
    for submodule in maven_modules.get('submodules', []):
        g, a, v = get_matching_gav(artifact_id, submodule)
        if g != None:
            return g, a, v
    return None, None, None

def cluster_releases(diffoscope_json_files, maven_modules, version, root):
    maven_releases = []
    cache = {}

    for diffoscope_json_file in diffoscope_json_files:
        artifact_id_from_diffoscope_file = extract_artifact_id(diffoscope_json_file, version)
        g, a, v = None, None, None
        
        # Retrieve GAV either from cache or using `get_matching_gav`
        if artifact_id_from_diffoscope_file not in cache:
            g, a, v = get_matching_gav(artifact_id_from_diffoscope_file, maven_modules)
            cache[artifact_id_from_diffoscope_file] = (g, a, v)
        else:
            g, a, v = cache[artifact_id_from_diffoscope_file]
        
        existing_entry = next((release for release in maven_releases if release["gav"] == f"{g}:{a}:{v}"), None)
        if existing_entry:
            existing_entry["unreproducible_artifacts"].append(diffoscope_json_file)
        else:
            maven_releases.append({
                "gav": f"{g}:{a}:{v}",
                "unreproducible_artifacts": [diffoscope_json_file]
            })
    
    for release in maven_releases:
        release["unreproducible_artifacts"] = list(set(release["unreproducible_artifacts"]))
    
    return maven_releases
        

def main():
    maven_projects = []
    args = parse_args()
    base_level = len(args.base_dir.split(os.path.sep))
    for root, dirs, files in os.walk(args.base_dir):
        for directory in dirs:
            current_level = len(root.split(os.path.sep))
            if current_level - base_level == 2:
                gav = get_GAV(os.path.join(root, directory))
                diffoscope_json_files = glob.glob("*.diffoscope.json", root_dir=os.path.join(root, directory))
                if len(diffoscope_json_files) == 0:
                    continue
                with open(os.path.join(root, directory, "output.json"), "r") as f:
                    maven_modules = json.load(f)
            
                maven_releases = cluster_releases(diffoscope_json_files, maven_modules, directory, root)
                maven_projects.append({
                    "name": gav,
                    "maven_releases": maven_releases
                })

    json.dump(maven_projects, open("unreproducible_maven_projects_to_releases-1.json", "w"), indent=2)
                    
            

if __name__ == "__main__":
    main()