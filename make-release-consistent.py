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
    # Only process .jar files
    if not artifact_name.endswith('.jar'):
        return None
    
    # Remove the version and .jar extension, and handle sources.jar
    cleaned_name = re.sub(r'-test-sources.jar', '.jar', artifact_name)
    cleaned_name = re.sub(r'-sources.jar', '.jar', cleaned_name)
    cleaned_name = re.sub(r'-tests.jar', '.jar', cleaned_name)
    cleaned_name = re.sub(r'-javadoc.jar', '.jar', cleaned_name)
    cleaned_name = re.sub(r'-jar.jar', '.jar', cleaned_name)
    cleaned_name = re.sub(r'-shaded.jar', '.jar', cleaned_name)
    cleaned_name = re.sub(r'-standalone.jar', '.jar', cleaned_name)
    cleaned_name = re.sub(r'-osgi.jar', '.jar', cleaned_name)
    cleaned_name = cleaned_name.replace(f"-{version}", "")
    cleaned_name = cleaned_name.replace(".jar", "")
    return cleaned_name

def total_classfiles(root_dir, artifact_name, source):
    path = os.path.join(root_dir, source.value, artifact_name)
    try:
        jar_file = zipfile.ZipFile(path)
        return sum(1 for _ in jar_file.namelist() if _.endswith('.class'))
    except FileNotFoundError:
        logging.warning(f"Artifact {artifact_name} missing {source.value}")
        return 0

def get_artifact_size(root_dir, artifact_name, source):
    # Get paths for both reference and rebuild
    ref_path = os.path.join(root_dir, source.value, artifact_name)
    
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
    reference_total_size = 0
    rebuild_total_size = 0

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
                                if not artifact_name.endswith('.jar'):
                                    continue
                                
                                # Verify reference and rebuild are same
                                if artifact.get("reference") != artifact.get("rebuild"):
                                    logging.warning(f"Reference Rebuild mismatch: {group_id}:{artifact_id}:{version} {artifact_name}")

                                reference_size = get_artifact_size(str(version_dir), artifact_name, ArtifactSource.REFERENCE)
                                rebuild_size = get_artifact_size(str(version_dir), artifact_name, ArtifactSource.REBUILD)
                                reference_total_size += reference_size
                                rebuild_total_size += rebuild_size


                                extracted_artifact_id = extract_artifact_id(artifact_name, version)
                                if group_id == "org.apache.cxf.fediz" and extracted_artifact_id == "common":
                                    modified_group_id = "org.apache.cxf.fediz.examples.wsclientWebapp.webservice"

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
                                    gav_to_artifact_map[gav].append({
                                        "name": artifact_name,
                                        "jNorm": artifact.get('jNorm'),
                                        "reference_size": reference_size,
                                        "rebuild_size": rebuild_size,
                                        "reference_classfiles": total_classfiles(str(version_dir), artifact_name, ArtifactSource.REFERENCE),
                                        "rebuild_classfiles": total_classfiles(str(version_dir), artifact_name, ArtifactSource.REBUILD)
                                    })
                                    reference_artifact_path = os.path.join(str(version_dir), ArtifactSource.REFERENCE.value, artifact_name)
                                    rebuild_artifact_path = os.path.join(str(version_dir), ArtifactSource.REBUILD.value, artifact_name)
                                    gav_to_file_path_map[gav].append({
                                        "reference": reference_artifact_path if os.path.exists(reference_artifact_path) else None,
                                        "rebuild": rebuild_artifact_path if os.path.exists(rebuild_artifact_path) else None
                                    })
                                    
                    except json.JSONDecodeError:
                        continue

    return gav_to_artifact_map, reference_total_size, rebuild_total_size, gav_to_file_path_map

gav_map, reference_total_size, rebuild_total_size, gav_to_file_path_map = process_jnorm_summaries()

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
    f.write(f'Reference total size: {reference_total_size / 1024} KB\n')
    f.write(f'Rebuild total size: {rebuild_total_size / 1024} KB\n')
    f.write(f"GAV mapping saved to gav_to_artifact_map.json\n")
    f.write(f"GAV to file path mapping saved to gav_to_file_path_map.json\n")