import concurrent.futures
import os
import subprocess
import json
from pathlib import Path

MAX_WORKERS = os.cpu_count()
BASE_DIR = Path("results")


def get_path_from_artifact(artifact_path: Path) -> str:
    return artifact_path.name.split(":")[0]


def process_pair(reference: Path, rebuild: Path, version_dir: Path):
    print(f"Processing: {reference} and {rebuild}")

    try:
        cmd = [
            "docker", "run",
            "-w", "/mnt",
            "--mount", f"type=bind,source={reference.resolve()},target=/reference.jar",
            "--mount", f"type=bind,source={rebuild.resolve()},target=/rebuild.jar",
            "-v", f"{version_dir.resolve()}:/mnt",
            "algomaster99/daleq:latest",
            "-j1", "/reference.jar",
            "-j2", "/rebuild.jar",
            "-o", f"/mnt/daleq/{get_path_from_artifact(reference)}/"
        ]
        print(cmd)


        process = subprocess.run(cmd, capture_output=True, text=True)
        exit_code_map = {"diff": process.returncode}

        daleq_dir = version_dir / "daleq"
        daleq_dir.mkdir(parents=True, exist_ok=True)
        json_file = daleq_dir / f"{get_path_from_artifact(reference)}.json"
        json_file.write_text(json.dumps(exit_code_map) + "\n")

        base_name = get_path_from_artifact(reference)
        log_file = daleq_dir / f"{base_name}.log"
        log_file.write_text(process.stdout + "\n" + process.stderr)

    except Exception as e:
        with open("/tmp/error.txt", "a") as f:
            f.write(str(e) + "\n")


def main():
    with open("gradle_projects_with_jvm_differences.txt") as f:
        gavs = set(line.strip() for line in f)

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = []

        for path in BASE_DIR.rglob("*"):
            if not path.is_dir():
                continue
            if len(path.parts) != len(BASE_DIR.parts) + 3:
                continue
            if path.name == "buildcache":
                continue

            operands = Operands.from_test_directory(path)

            gav = f"{operands.group_id}:{operands.artifact_id}:{operands.version}"
            if gav in gavs:
                for ref, reb in operands.reference_rebuild_pairs:
                    daleq_dir = operands.version_dir / "daleq"
                    ref_path = daleq_dir / get_path_from_artifact(ref)
                    json_path = ref_path.with_suffix(".json")

                    if ref_path.exists() and json_path.exists():
                        print(gav)
                        continue

                    futures.append(executor.submit(process_pair, ref, reb, operands.version_dir))
            else:
                print(f"Skipping: {gav}")

        # wait for completion
        concurrent.futures.wait(futures)


# ----------------- Operands class -----------------
class Operands:
    REF_DIR = "reference"
    REB_DIR = "rebuild"

    def __init__(self, group_id, artifact_id, version, pairs, version_dir: Path):
        self.group_id = group_id
        self.artifact_id = artifact_id
        self.version = version
        self.reference_rebuild_pairs = pairs
        self.version_dir = version_dir

    @staticmethod
    def from_test_directory(version_dir: Path):
        artifact_id = version_dir.parent.name
        group_id = version_dir.parent.parent.name
        version = version_dir.name

        ref_dir = version_dir / Operands.REF_DIR
        reb_dir = version_dir / Operands.REB_DIR

        if not ref_dir.exists() or not reb_dir.exists():
            return Operands(group_id, artifact_id, version, [], version_dir)

        ref_files = {f.name for f in ref_dir.iterdir() if f.is_file()}
        reb_files = {f.name for f in reb_dir.iterdir() if f.is_file()}

        if ref_files != reb_files:
            return Operands(group_id, artifact_id, version, [], version_dir)

        pairs = []
        for f in ref_dir.iterdir():
            reb = reb_dir / f.name
            if reb.exists():
                pairs.append((f, reb))

        return Operands(group_id, artifact_id, version, pairs, version_dir)


if __name__ == "__main__":
    main()