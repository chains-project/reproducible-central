import json

# Read the JSON file
with open("make-release-consistent.json", "r") as f:
    data = json.load(f)

# Dictionary to store extensions and their jNorm values
extension_stats = {}
total_stats = {'total': 0, 'jnorm_0': 0, 'jnorm_1': 0, 'jnorm_2': 0}

# Analyze each artifact
for gav, artifacts in data.items():
    for artifact in artifacts:
        name = artifact['name']
        jnorm = artifact['jNorm']
        
        # Find the extension
        for ext in ['.tar.gz', '.gz', '.tar', '.rar', '.far', '.zip', '.war', '.mar', '.jar']:
            if name.endswith(ext):
                if ext not in extension_stats:
                    extension_stats[ext] = {'total': 0, 'jnorm_0': 0, 'jnorm_1': 0, 'jnorm_2': 0}
                
                extension_stats[ext]['total'] += 1
                extension_stats[ext][f'jnorm_{jnorm}'] += 1
                
                # Update totals
                total_stats['total'] += 1
                total_stats[f'jnorm_{jnorm}'] += 1
                break

# Print results
print("Extension Statistics:")
print("\nExt\tTotal\tjNorm 0\tjNorm 1\tjNorm 2\tSuccess Rate")
print("-" * 60)
for ext, stats in extension_stats.items():
    success_rate = (stats['jnorm_0'] / stats['total'] * 100) if stats['total'] > 0 else 0
    print(f"{ext}\t{stats['total']}\t{stats['jnorm_0']}\t{stats['jnorm_1']}\t{stats['jnorm_2']}\t{success_rate:.1f}%")

# Print totals
print("-" * 60)
total_success_rate = (total_stats['jnorm_0'] / total_stats['total'] * 100) if total_stats['total'] > 0 else 0
print(f"TOTAL\t{total_stats['total']}\t{total_stats['jnorm_0']}\t{total_stats['jnorm_1']}\t{total_stats['jnorm_2']}\t{total_success_rate:.1f}%") 