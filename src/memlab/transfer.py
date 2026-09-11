"""The transfer test (decision 003b).

Each raw note is handed, alone, to a fresh assistant drafting emails it has never
seen. The note transfers if it lifts some rule's pass count by at least
`min_gain` over the no-memory baseline. Baseline and note runs share seeds per
email, so the note is the only difference.
"""

from pathlib import Path

from .rules import RULES, check
from .session import draft
from .store import append_jsonl, iter_notes, read_jsonl, write_json


def run_transfer(config: dict, emails: list[dict], run: Path) -> None:
    model = config["assistant"]
    cfg = config["transfer"]
    heldout = [e for e in emails if e["split"] == "heldout"][: cfg["heldout"]]

    def log(stage, call):
        append_jsonl(run / "calls.jsonl", {"stage": stage, **call})

    def passes_with(memory: list[str]) -> dict[str, int]:
        counts = {rule: 0 for rule in RULES}
        for j, email in enumerate(heldout):
            grade = check(draft(model, memory, email, cfg["seed"] + j, log), email["answers"])
            for rule, ok in grade.items():
                counts[rule] += ok
        return counts

    baseline = passes_with([])
    write_json(run / "transfer_baseline.json", {"heldout": len(heldout), "passes": baseline})
    print(f"baseline on {len(heldout)} held-out emails: {baseline}")

    cache: dict[str, dict[str, int]] = {}  # identical notes are only tested once
    notes = list(iter_notes(read_jsonl(run / "sessions.jsonl")))
    for n, note in enumerate(notes, 1):
        if note["text"] not in cache:
            cache[note["text"]] = passes_with([note["text"]])
        passes = cache[note["text"]]
        gains = {rule: passes[rule] - baseline[rule] for rule in RULES}
        lifted = [rule for rule, g in gains.items() if g >= cfg["min_gain"]]
        append_jsonl(
            run / "transfer.jsonl",
            {**note, "passes": passes, "gains": gains, "transferred_rules": lifted, "transfers": bool(lifted)},
        )
        print(f"note {n}/{len(notes)}: {'transfers ' + ', '.join(lifted) if lifted else 'no transfer'}")
