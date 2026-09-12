"""Build the published results file the portfolio reads.

The schema is versioned: the portfolio pins a schema_version, so the harness can
change without silently breaking the page.
"""

from datetime import datetime, timezone
from pathlib import Path

from .label import TYPES, agreement
from .rules import RULES
from .store import iter_notes, read_json, read_jsonl, write_json

SCHEMA_VERSION = 1


def run_export(config: dict, run: Path) -> Path:
    sessions = read_jsonl(run / "sessions.jsonl")
    transfer = {t["note_id"]: t for t in read_jsonl(run / "transfer.jsonl")}
    labels = {l["note_id"]: l["type"] for l in read_jsonl(run / "labels.jsonl")}
    baseline = read_json(run / "transfer_baseline.json") or {}
    hand = read_json(run / "hand_labels.json") or {}
    control = read_jsonl(run / "transfer_control.jsonl")

    arms = {}
    for arm in config["arms"]:
        arm_sessions = [s for s in sessions if s["arm"] == arm]
        notes = [n for n in iter_notes(arm_sessions)]
        by_type = {t: {"notes": 0, "transferred": 0} for t in TYPES}
        for note in notes:
            t = labels.get(note["note_id"])
            if t:
                by_type[t]["notes"] += 1
                by_type[t]["transferred"] += bool(transfer.get(note["note_id"], {}).get("transfers"))
        arms[arm] = {
            "sessions": len(arm_sessions),
            "raw_notes": len(notes),
            "by_type": by_type,
            "rules_captured": sorted(
                {r for n in notes for r in transfer.get(n["note_id"], {}).get("transferred_rules", [])}
            ),
            "first_draft_rules_passed": [sum(s["grade"].values()) for s in arm_sessions],
            "curated_memory_final": len(arm_sessions[-1]["memory_after"]) if arm_sessions else 0,
            "curation_ops": {
                "applied": sum(len(s["operations_applied"]) for s in arm_sessions),
                "rejected": sum(len(s["operations_rejected"]) for s in arm_sessions),
            },
        }

    result = {
        "schema_version": SCHEMA_VERSION,
        "experiment": "q1-extraction",
        "run": config["name"],
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "config": {k: config[k] for k in ("assistant", "labeler", "arms", "sessions", "transfer")},
        "rules": RULES,
        "transfer_baseline": baseline,
        "arms": arms,
        "noise_floor": {
            "control_notes": len(control),
            "transferred": sum(c["transfers"] for c in control),
        },
        "labeler_agreement": agreement(labels, hand),
        "caveats": [
            "One local 8B model (qwen3:8b). A larger model may extract differently.",
            "About 20 sessions per arm, so results are directional, not conclusive.",
            "The user is scripted, so conversations are less varied than real use.",
        ],
    }
    out = Path("results") / f"{config['name']}.json"
    write_json(out, result)
    return out
