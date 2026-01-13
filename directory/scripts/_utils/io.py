from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def dump_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        # Use 2-space indentation for human-friendly diffs in GitHub PRs.
        json.dump(obj, f, indent=2, ensure_ascii=False, sort_keys=True)
        f.write("\n")
