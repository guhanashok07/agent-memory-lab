"""Run files. Everything a stage produces is plain JSON on disk, committed with the results."""

import json
from pathlib import Path


def run_dir(config: dict) -> Path:
    path = Path("runs") / config["name"]
    path.mkdir(parents=True, exist_ok=True)
    return path


def append_jsonl(path: Path, obj: dict) -> None:
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def iter_notes(sessions: list[dict]):
    """Every raw reflection note, with a stable id: <arm>-<session>-<index>."""
    for s in sessions:
        for k, text in enumerate(s["notes"]):
            yield {
                "note_id": f"{s['arm']}-{s['session']:02d}-{k}",
                "arm": s["arm"],
                "session": s["session"],
                "text": text,
            }
