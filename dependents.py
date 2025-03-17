import requests
import json

def get_dependents(gav):
    group_id, artifact_id, version = gav.split(':')
    purl = f"pkg:maven/{group_id}/{artifact_id}@{version}"
    url = "https://central.sonatype.com/api/internal/browse/dependents"
    data = {
        "purl": purl,
        "page": 0,
        "size": 10,
        "searchTerm": "",
        "filter": ["dependencyRef:DIRECT"]
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.json()["totalResultCount"]

def main():
    gav_to_total_dependents = []
    with open('projects_with_jvm_differences.txt', 'r') as file:
        gavs = file.readlines()
    
    for gav in gavs:
        gav = gav.strip()
        if gav:
            dependents = get_dependents(gav)
            gav_to_total_dependents.append({
                "gav": gav,
                "totalDependents": dependents
            })
    
    with open('gav_to_total_dependents.json', 'w+') as file:
        json.dump(gav_to_total_dependents, file, indent=4)
        

if __name__ == "__main__":
    main()