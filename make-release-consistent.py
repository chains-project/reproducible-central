import json
import os
from pathlib import Path
import requests
import re
from time import sleep
import logging
from enum import Enum
import zipfile

# Set up logging
logging.basicConfig(
    filename='make-release-consistent.log',
    level=logging.WARNING,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class ArtifactSource(Enum):
    REBUILD = "rebuild"
    REFERENCE = "reference"

def check_maven_central(group_id, artifact_id, version):
    url = f"https://repo1.maven.org/maven2/{group_id.replace('.', '/')}/{artifact_id}/{version}"
    response = requests.get(url)
    # Sleep to be nice to mvnrepository
    return response.status_code == 200

def extract_artifact_id(artifact_name, version):
    # Get the extension
    for ext in ['.zip','.jar']:
        if artifact_name.endswith(ext):
            # Find where version starts
            version_start = artifact_name.find(f"-{version}")
            if version_start != -1:
                # Keep everything before version, don't add extension
                return artifact_name[:version_start]
    
    return None
    

    # Check if both files exist and get their sizes
    if os.path.exists(ref_path):
        ref_size = os.path.getsize(ref_path)
        return ref_size
    else:
        logging.warning(f"Missing {source} file: {ref_path}")
        return 0

    # Check if both files exist and get their sizes
    if os.path.exists(ref_path):
        ref_size = os.path.getsize(ref_path)
        return ref_size
    else:
        logging.warning(f"Missing {source} file: {ref_path}")
        return 0

def process_jnorm_summaries():
    base_dir = "from-repairnator"
    gav_to_artifact_map = {}
    gav_to_file_path_map = {}

    for root, _, files in os.walk(base_dir):
        for file in files:
            if file == "jNorm_summary.json":
                file_path = Path(root) / file
                version_dir = file_path.parent.parent
                
                with open(file_path) as f:
                    try:
                        data = json.load(f)
                        if "gav" in data:
                            group_id, artifact_id, version = data["gav"].split(":")
                            
                            for artifact in data.get("artifacts", []):
                                # reset group_id to original value
                                modified_group_id = group_id
                                artifact_name = artifact.get("artifact_name", "")
                                
                                # Skip if not a jar file
                                if not artifact_name.endswith('.jar') and not artifact_name.endswith('.zip'):
                                    continue
                                
                                # Verify reference and rebuild are same
                                if artifact.get("reference") != artifact.get("rebuild"):
                                    logging.warning(f"Reference Rebuild mismatch: {group_id}:{artifact_id}:{version} {artifact_name}")



                                extracted_artifact_id = extract_artifact_id(artifact_name, version)
                                if group_id == "org.apache.cxf.fediz":
                                    possible_group_ids = ["org.apache.cxf.fediz", "org.apache.cxf.fediz.examples.wsclientWebapp.webservice", "org.apache.cxf.fediz.examples", "org.apache.cxf.fediz.examples.wsclientWebapp", "org.apache.cxf.fediz.systests.webapps"]
                                    for candidate_group_id in possible_group_ids:
                                        if check_maven_central(candidate_group_id, extracted_artifact_id, version):
                                            modified_group_id = candidate_group_id
                                            break
                                    else:
                                        logging.warning(f"Failed to find artifact in Maven Central: {group_id}:{extracted_artifact_id}:{version}")
                                        continue

                                if group_id == "org.apache.hive" and extracted_artifact_id == "hive-webhcat":
                                    modified_group_id = "org.apache.hive.hcatalog"

                                if group_id == "org.apache.drill":
                                    possible_group_ids = ['org.apache.drill', 'org.apache.drill.contrib', 'org.apache.drill.exec', 'org.apache.drill.memory', 'org.apache.drill.metastore', 'org.apache.drill.contrib.data', 'org.apache.drill.tools', 'org.apache.drill.contrib.storage-hive']
                                    for candidate_group_id in possible_group_ids:
                                        if check_maven_central(candidate_group_id, extracted_artifact_id, version):
                                            modified_group_id = candidate_group_id
                                            break
                                    else:
                                        logging.warning(f"Failed to find artifact in Maven Central: {group_id}:{extracted_artifact_id}:{version}")
                                        continue

                                if group_id != "org.apache.drill" and not check_maven_central(modified_group_id, extracted_artifact_id, version):
                                    logging.warning(f"Failed to find artifact in Maven Central: {modified_group_id}:{extracted_artifact_id}:{version}")
                                    continue
                                
                                if extracted_artifact_id:
                                    gav = f"{modified_group_id}:{extracted_artifact_id}:{version}"
                                    
                                    if gav not in gav_to_artifact_map:
                                        gav_to_artifact_map[gav] = []
                                        gav_to_file_path_map[gav] = []

                                    reference_artifact_path = os.path.join(str(version_dir), ArtifactSource.REFERENCE.value, artifact_name)
                                    original_artifact_name = artifact_name
                                    if 'dependency-check-cli' in reference_artifact_path:
                                        artifact_name = artifact_name.replace('-cli', '')
                                    elif 'drill-hive-exec-shaded' in reference_artifact_path:
                                        artifact_name = artifact_name.replace('-jar', '')
                                    
                                    gav_to_artifact_map[gav].append({
                                        "name": original_artifact_name,
                                        "jNorm": artifact.get('jNorm'),
                                    })
                                    rebuild_artifact_path = os.path.join(str(version_dir), ArtifactSource.REBUILD.value, artifact_name)
                                    gav_to_file_path_map[gav].append({
                                        "reference": reference_artifact_path if os.path.exists(reference_artifact_path) else None,
                                        "rebuild": rebuild_artifact_path if os.path.exists(rebuild_artifact_path) else None
                                    })
                                    
                    except json.JSONDecodeError:
                        continue

    return gav_to_artifact_map, gav_to_file_path_map

gav_map, gav_to_file_path_map = process_jnorm_summaries()

unique_maven_central_releases = set()
for artifact in gav_map.keys():
    unique_maven_central_releases.add(':'.join(artifact.split(':')[:2]))

with open('make-release-consistent.json', 'w') as f:
    json.dump(gav_map, f, indent=2)

with open('make-release-consistent-file-paths.json', 'w') as f:
    json.dump(gav_to_file_path_map, f, indent=2)

with open('make-release-consistent.txt', 'w') as f:
    f.write(f'{len(gav_map)} unique GAVs found\n')
    f.write(f'{sum(len(artifacts) for artifacts in gav_map.values())} artifacts found\n')
    f.write(f'{len(unique_maven_central_releases)} unique Maven Central releases found\n')
    f.write(f"GAV mapping saved to gav_to_artifact_map.json\n")
    f.write(f"GAV to file path mapping saved to gav_to_file_path_map.json\n")