import os
import subprocess
import sys
from pathlib import Path
from typing import Any
import frontmatter


def check_name(metadata: dict[str, Any]):
    name = metadata.get("name")
    if not name:
        raise ValueError("name is required")


def check_description(metadata: dict[str, Any]):
    description = metadata.get("description")
    if not description:
        raise ValueError("description is required")


def check_senarios(metadata: dict[str, Any]):
    senarios = metadata.get("senarios")
    if not senarios:
        raise ValueError("senarios is required")
    if len(senarios) != 4:
        raise ValueError("senarios should have 4 items")


def check_components(metadata: dict[str, Any]):
    standard_components = ["Identity", "MCP Toolset"]
    components = metadata.get("components")
    if not components:
        raise ValueError("components is required")
    if len(components) == 0:
        raise ValueError("components should have at least 1 item")
    for component in components:
        name = component.get("name")
        if not name:
            raise ValueError("component name is required")
        desc = component.get("desc")
        if not desc:
            raise ValueError("component desc is required")
        if component["name"] not in standard_components:
            raise ValueError(f"component name should be one of {standard_components}")


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


def check_readme_file(path: Path) -> None:
    post = frontmatter.load(path)
    check_name(post.metadata)
    check_description(post.metadata)
    check_senarios(post.metadata)
    check_components(post.metadata)


def main() -> None:
    args = sys.argv[1:]
    if args:
        readme_paths = [Path(p) for p in args]
    else:
        base_sha = os.environ.get("BASE_SHA", "")
        head_sha = os.environ.get("HEAD_SHA", "")
        changed = get_changed_files(base_sha, head_sha)
        readme_paths = [Path(p) for p in changed if Path(p).name.lower() == "readme.md"]

    if not readme_paths:
        print("No README.md files to check, skipping.")
        return

    failed: list[Path] = []

    for path in readme_paths:
        if not path.is_file():
            print(f"File not found, skipping: {path}")
            continue
        try:
            print(f"Checking README metadata in: {path}")
            check_readme_file(path)
        except Exception as exc:
            sys.stderr.write(f"Validation failed for {path}: {exc}\n")
            failed.append(path)

    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
