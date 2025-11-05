# capture_latest_post.py
import json
import os
from pathlib import Path

path = Path("latest_post.json")
if not path.exists():
    print("has_latest=false")
    exit(0)

with path.open(encoding="utf-8") as f:
    data = json.load(f)

out_path = Path(os.environ["GITHUB_OUTPUT"])
with out_path.open("a", encoding="utf-8") as out:
    for key in ("title", "velog_url", "site_url", "filename"):
        value = data.get(key, "")
        out.write(f"{key}<<EOF\n{value}\nEOF\n")

path.unlink()