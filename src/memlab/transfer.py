"""The transfer test (decision 003), and its noise floor (decision 018).

Each raw note is handed, alone, to a fresh assistant drafting emails it has never
seen. The note transfers if it lifts some rule's pass count by at least
`min_gain` over the no-memory baseline. Baseline and note runs share seeds per
email, so the note is the only difference.

Any note in the prompt nudges the model's style a little, so the same test is
also run on irrelevant control notes ("G uses a MacBook"). Their transfer rate is
the floor every real rate is read against.
"""

import json
from pathlib import Path

from .rules import RULES, check
from .session import draft
from .store import append_jsonl, iter_notes, read_json, read_jsonl, write_json


def _heldout(config: dict, emails: list[dict]) -> list[dict]:
    return [e for e in emails if e["split"] == "heldout"][: config["transfer"]["heldout"]]


def _passes(config: dict, heldout: list[dict], memory: list[str], run: Path) -> dict[str, int]:
    def log(stage, call):
        append_jsonl(run / "calls.jsonl", {"stage": stage, **call})

    counts = {rule: 0 for rule in RULES}
    for j, email in enumerate(heldout):
        text = draft(config["assistant"], memory, email, config["transfer"]["seed"] + j, log)
        for rule, ok in check(text, email["answers"]).items():
            counts[rule] += ok
    return counts


def _verdict(passes: dict[str, int], baseline: dict[str, int], min_gain: int) -> dict:
    gains = {rule: passes[rule] - baseline[rule] for rule in RULES}
    lifted = [rule for rule, g in gains.items() if g >= min_gain]
    return {"passes": passes, "gains": gains, "transferred_rules": lifted, "transfers": bool(lifted)}


def run_transfer(config: dict, emails: list[dict], run: Path) -> None:
    heldout = _heldout(config, emails)
    baseline = _passes(config, heldout, [], run)
    write_json(run / "transfer_baseline.json", {"heldout": len(heldout), "passes": baseline})
    print(f"baseline on {len(heldout)} held-out emails: {baseline}")

    cache: dict[str, dict[str, int]] = {}  # identical notes are only tested once
    notes = list(iter_notes(read_jsonl(run / "sessions.jsonl")))
    for n, note in enumerate(notes, 1):
        if note["text"] not in cache:
            cache[note["text"]] = _passes(config, heldout, [note["text"]], run)
        verdict = _verdict(cache[note["text"]], baseline, config["transfer"]["min_gain"])
        append_jsonl(run / "transfer.jsonl", {**note, **verdict})
        print(f"note {n}/{len(notes)}: {', '.join(verdict['transferred_rules']) or 'no transfer'}")


def run_control(config: dict, emails: list[dict], run: Path) -> None:
    baseline = read_json(run / "transfer_baseline.json")
    if baseline is None:
        raise SystemExit("Run the transfer stage first; the control reuses its baseline.")
    heldout = _heldout(config, emails)
    notes = json.loads(Path(config["transfer"]["control_notes"]).read_text())
    for n, text in enumerate(notes, 1):
        verdict = _verdict(_passes(config, heldout, [text], run), baseline["passes"], config["transfer"]["min_gain"])
        append_jsonl(run / "transfer_control.jsonl", {"text": text, **verdict})
        print(f"control {n}/{len(notes)}: {', '.join(verdict['transferred_rules']) or 'no transfer'}")
