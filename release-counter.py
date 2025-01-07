import argparse
import os

def parse_args():
    parser = argparse.ArgumentParser(description='Process release consistency')
    parser.add_argument('--base-dir', 
                       default="release-counter",
                       help='Base directory for processing (default: release-counter)')
    return parser.parse_args()

def load_success_builds():
    path_to_file = os.path.join('diffoscope-failures', "all_success.txt")
    with open(path_to_file, 'r') as f:
        return set([line.strip() for line in f.readlines()])

def get_GAV(path_to_output):
    _, group_id, artifact_id, version, _ = path_to_output.split(os.path.sep)
    return f"{group_id}:{artifact_id}:{version}"

def main():
    total = 0
    args = parse_args()
    base_level = len(args.base_dir.split(os.path.sep))
    success_builds = load_success_builds()
    for root, dirs, files in os.walk(args.base_dir):
        for file in files:
            current_level = len(root.split(os.path.sep))
            if current_level - base_level == 3 and file.endswith("output.txt"):
                gav = get_GAV(os.path.join(root, file))
                if gav in success_builds:
                    with open(os.path.join(root, file), 'r') as f:
                        data = [i.strip() for i in f.readlines()]
                    total += len(data)
    print(total)

if __name__ == "__main__":
    main()
