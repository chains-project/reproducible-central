import json
import requests
from urllib.parse import quote
import time
from tqdm import tqdm

def construct_pom_url(group_id, artifact_id, version):
    group_path = group_id.replace('.', '/')
    return f"https://repo1.maven.org/maven2/{quote(group_path)}/{quote(artifact_id)}/{quote(version)}/{quote(artifact_id)}-{quote(version)}.pom"

def check_pom_existence(url):
    try:
        response = requests.head(url, timeout=10)
        return response.status_code == 200
    except requests.RequestException:
        return False

with open('make-release-consistent.json', 'r') as f:
    gav_map = json.load(f)

total_gavs = 0
missing_poms = []

print("Checking POM files...")
for gav in tqdm(gav_map.keys()):
    group_id, artifact_id, version = gav.split(':')
    pom_url = construct_pom_url(group_id, artifact_id, version)
    
    total_gavs += 1
    
    if not check_pom_existence(pom_url):
        missing_poms.append({
            'gav': gav,
            'url': pom_url
        })
    
print(f"\nTotal GAVs checked: {total_gavs}")
print(f"GAVs missing POM files: {len(missing_poms)}")

if missing_poms:
    with open('missing_poms.json', 'w') as f:
        json.dump(missing_poms, f, indent=2)
    print(f"Missing POM details saved to 'missing_poms.json'") 
