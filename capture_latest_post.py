from __future__ import annotations

import json
import os
import sys
from pathlib import Path

OUTPUT_KEYS = ("title", "velog_url", "site_url", "filename")


def write_output_line(handle, key: str, value: str) -> None:
    """Write a multi-line GitHub Action output entry."""
    handle.write(f"{key}<<EOF\n{value}\nEOF\n")


def main() -> int:
    output_path = Path(os.environ["GITHUB_OUTPUT"])
    metadata_path = Path("latest_post.json")

    if not metadata_path.exists():
        with output_path.open("a", encoding="utf-8") as handle:
            handle.write("has_latest=false\n")
        return 0

    with metadata_path.open(encoding="utf-8") as source:
        data = json.load(source)

    with output_path.open("a", encoding="utf-8") as handle:
        handle.write("has_latest=true\n")
        for key in OUTPUT_KEYS:
            value = str(data.get(key, "") or "")
            write_output_line(handle, key, value)

    metadata_path.unlink()
    return 0


if __name__ == "__main__":
    sys.exit(main())
