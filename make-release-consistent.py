import json
import os
from pathlib import Path
import requests
import re
from time import sleep
import logging

# Set up logging
logging.basicConfig(
    filename='maven_check_failures.log',
    level=logging.WARNING,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

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

def process_jnorm_summaries():
    base_dir = "from-repairnator"
    gav_to_artifact_map = {}  # New map for GAV to artifact name mapping

    for root, _, files in os.walk(base_dir):
        for file in files:
            if file == "jNorm_summary.json":
                file_path = Path(root) / file
                
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
                                    Exception(f"Error: reference and rebuild mismatch for {artifact_name}")

                                extracted_artifact_id = extract_artifact_id(artifact_name, version)
                                
                                if extracted_artifact_id:
                                    gav = f"{group_id}:{extracted_artifact_id}:{version}"
                                    
                                    # Add to mapping as a list
                                    if gav not in gav_to_artifact_map:
                                        gav_to_artifact_map[gav] = []
                                    gav_to_artifact_map[gav].append({
                                        "artifact_name": artifact_name,
                                        "jNorm": artifact.get("jNorm")
                                    })
                                    
                                    if group_id == "org.apache.cxf.fediz" and extracted_artifact_id == "common":
                                        modified_group_id = "org.apache.cxf.fediz.examples.wsclientWebapp.webservice"
                                    
                                    if group_id == "org.apache.hive" and extracted_artifact_id == "hive-webhcat":
                                        modified_group_id = "org.apache.hive.hcatalog"

                                    if group_id == "org.apache.drill":
                                        possible_group_ids = ['org.apache.drill', 'org.apache.drill.contrib', 'org.apache.drill.exec', 'org.apache.drill.memory', 'org.apache.drill.metastore', 'org.apache.drill.contrib.data', 'org.apache.drill.tools', 'org.apache.drill.contrib.storage-hive']
                                        for candidate_group_id in possible_group_ids:
                                            if check_maven_central(candidate_group_id, extracted_artifact_id, version):
                                                break
                                        else:
                                            logging.warning(f"Failed to find artifact in Maven Central: {group_id}:{extracted_artifact_id}:{version}")
                                    
                                    if group_id != "org.apache.drill" and not check_maven_central(modified_group_id, extracted_artifact_id, version):
                                        logging.warning(f"Failed to find artifact in Maven Central: {modified_group_id}:{extracted_artifact_id}:{version}")
                                    
                    except json.JSONDecodeError:
                        continue

    return gav_to_artifact_map

gav_map = process_jnorm_summaries()

unique_maven_central_releases = set()
for artifact in gav_map.keys():
    unique_maven_central_releases.add(':'.join(artifact.split(':')[:2]))

with open('make-release-consistent.json', 'w') as f:
    json.dump(gav_map, f, indent=2)

with open('make-release-consistent.txt', 'w') as f:
    f.write(f'{len(gav_map)} unique GAVs found\n')
    f.write(f'{sum(len(artifacts) for artifacts in gav_map.values())} artifacts found\n')
    f.write(f'{len(unique_maven_central_releases)} unique Maven Central releases found\n')
    f.write(f"GAV mapping saved to gav_to_artifact_map.json\n")
