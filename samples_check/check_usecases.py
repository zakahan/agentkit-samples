import os
import subprocess
import sys
from pathlib import Path


def get_changed_files(base_sha: str, head_sha: str) -> list[str]:
    if not base_sha or not head_sha:
        return []
    try:
        output = subprocess.check_output(
            ["git", "diff", "--name-only", base_sha, head_sha],
            text=True,
            stderr=subprocess.STDOUT,
        )
    except subprocess.CalledProcessError as exc:
        sys.stderr.write(exc.output)
        return []
    return [line.strip() for line in output.splitlines() if line.strip()]


def main() -> None:
    base_sha = os.environ.get("BASE_SHA", "")
    head_sha = os.environ.get("HEAD_SHA", "")

    changed = get_changed_files(base_sha, head_sha)
    changed_use_cases = [p for p in changed if p.startswith("02-use-cases/")]

    if not changed_use_cases:
        print("No changes under 02-use-cases, skipping main.py checks.")
        return

    candidate_dirs: set[Path] = set()
    for rel_path in changed_use_cases:
        parts = Path(rel_path).parts
        if len(parts) >= 2 and parts[0] == "02-use-cases":
            candidate_dirs.add(Path(parts[0]) / parts[1])

    if not candidate_dirs:
        print(
            "No top-level 02-use-cases/* directories detected, skipping main.py checks."
        )
        return

    print("Use-case directories to check:")
    for d in sorted(candidate_dirs):
        print(f"  - {d}")

    failed_dirs: list[Path] = []

    for d in sorted(candidate_dirs):
        main_py = d / "main.py"
        if main_py.is_file():
            print(f"Running python main.py in {d}")
            result = subprocess.run(
                [sys.executable, "main.py"],
                cwd=str(d),
            )
            if result.returncode != 0:
                failed_dirs.append(d)
        else:
            print(f"No main.py in {d}, skipping.")

    if failed_dirs:
        sys.stderr.write(
            "main.py checks failed in directories: "
            + ", ".join(str(d) for d in failed_dirs)
            + "\n"
        )
        raise SystemExit(1)


if __name__ == "__main__":
    main()
