import json

# Read the JSON file
with open("make-release-consistent.json", "r") as f:
    data = json.load(f)

# Initialize lists for different jNorm categories
gavs_all_0 = []  # GAVs where all artifacts have jNorm 0
gavs_failed = []  # GAVs where at least one artifact has jNorm 1 or 2

# Analyze each GAV
for gav, artifacts in data.items():
    # Get all jNorm values for this GAV
    jnorm_values = [artifact.get('jNorm') for artifact in artifacts]
    
    # Classify GAV based on jNorm values
    if all(jnorm == 0 for jnorm in jnorm_values):
        gavs_all_0.append(gav)
    elif any(jnorm in [1, 2] for jnorm in jnorm_values):
        gavs_failed.append((gav, artifacts))

# Print results
print(f"GAVs with all jNorm 0: {len(gavs_all_0)}")
for gav in gavs_all_0:
    print(gav)

print(f"\nGAVs with jNorm 1 or 2 (Failed Normalization): {len(gavs_failed)}")
for gav, artifacts in gavs_failed:
    print(f"\n{gav}")
    for artifact in artifacts:
        if artifact['jNorm'] in [1, 2]:
            print(f"   {artifact['name']}, jNorm: {artifact['jNorm']}")

