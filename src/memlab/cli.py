"""memlab <stage> [--config PATH] [--force]

Stages run in order and each reads the previous stage's files, so a crashed run
resumes from the last finished stage.
"""

import argparse
import json
import os
from pathlib import Path

from . import ollama
from .export import run_export
from .label import run_handlabel, run_labels
from .session import run_pilot, run_sessions
from .store import run_dir, write_json
from .transfer import run_transfer

OUTPUTS = {
    "pilot": ["pilot.jsonl", "pilot_calls.jsonl"],
    "sessions": ["sessions.jsonl"],
    "transfer": ["transfer.jsonl", "transfer_baseline.json"],
    "label": ["labels.jsonl"],
}


def _load_env(path: str = ".env") -> None:
    if not os.path.exists(path):
        return
    for line in Path(path).read_text().splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


def _ready(run: Path, stage: str, force: bool) -> bool:
    files = [run / f for f in OUTPUTS.get(stage, [])]
    if any(f.exists() for f in files):
        if not force:
            print(f"{stage}: already done in {run}. Use --force to redo it.")
            return False
        for f in files:
            f.unlink(missing_ok=True)
    return True


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="memlab")
    parser.add_argument("stage", choices=["pilot", "sessions", "transfer", "label", "handlabel", "export", "all"])
    parser.add_argument("--config", default="configs/q1-extraction-v1.json")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)

    _load_env()
    config = json.loads(Path(args.config).read_text())
    emails = json.loads(Path(config["emails"]).read_text())
    run = run_dir(config)
    write_json(run / "config.json", config)

    stages = ["sessions", "transfer", "label", "export"] if args.stage == "all" else [args.stage]
    if any(s in ("pilot", "sessions", "transfer", "label") for s in stages):
        ollama.verify_pins(config["assistant"], config["labeler"])

    for stage in stages:
        if not _ready(run, stage, args.force):
            continue
        if stage == "pilot":
            rates = run_pilot(config, emails, run)
            print("\nNo-memory pass rate per rule:")
            for rule, rate in rates.items():
                print(f"  {rule:<18} {rate:.0%}")
        elif stage == "sessions":
            run_sessions(config, emails, run)
        elif stage == "transfer":
            run_transfer(config, emails, run)
        elif stage == "label":
            run_labels(config, run)
        elif stage == "handlabel":
            run_handlabel(config, run)
        elif stage == "export":
            print(f"Wrote {run_export(config, run)}")


if __name__ == "__main__":
    main()
