"""Note types: a model labeler, plus blind hand labels to check it against."""

import random
from pathlib import Path

from . import ollama, prompts
from .store import append_jsonl, iter_notes, read_jsonl, write_json

TYPES = ("episodic", "semantic", "procedural")


def run_labels(config: dict, run: Path) -> None:
    labeler = config["labeler"]
    cache: dict[str, str] = {}
    for note in iter_notes(read_jsonl(run / "sessions.jsonl")):
        if note["text"] not in cache:
            label, call = ollama.chat_json(
                labeler,
                [
                    {"role": "system", "content": prompts.LABEL_SYSTEM},
                    {"role": "user", "content": prompts.LABEL_TASK.format(note=note["text"])},
                ],
                seed=config["labeler_seed"],
                schema=prompts.LABEL_SCHEMA,
            )
            append_jsonl(run / "calls.jsonl", {"stage": "label", **call})
            cache[note["text"]] = label["type"]
        append_jsonl(run / "labels.jsonl", {**note, "type": cache[note["text"]]})


def run_handlabel(config: dict, run: Path) -> None:
    """Interactive. Shows a fixed random sample of notes without the model's label,
    so the human judgment is independent."""
    notes = list(iter_notes(read_jsonl(run / "sessions.jsonl")))
    cfg = config["handlabel"]
    sample = random.Random(cfg["seed"]).sample(notes, min(cfg["sample"], len(notes)))
    keys = {"e": "episodic", "s": "semantic", "p": "procedural"}
    labels: dict[str, str] = {}
    print(prompts.LABEL_TASK.split("Note:")[0])
    for i, note in enumerate(sample, 1):
        while True:
            answer = input(f"\n[{i}/{len(sample)}] {note['text']}\n  e / s / p > ").strip().lower()
            if answer in keys:
                labels[note["note_id"]] = keys[answer]
                break
    write_json(run / "hand_labels.json", labels)
    print(f"Saved {len(labels)} labels.")


def agreement(machine: dict[str, str], human: dict[str, str]) -> dict | None:
    """Percent agreement and Cohen's kappa, which discounts agreement expected by chance."""
    ids = [i for i in human if i in machine]
    if not ids:
        return None
    n = len(ids)
    observed = sum(machine[i] == human[i] for i in ids) / n
    expected = sum(
        (sum(machine[i] == t for i in ids) / n) * (sum(human[i] == t for i in ids) / n) for t in TYPES
    )
    kappa = (observed - expected) / (1 - expected) if expected < 1 else 1.0
    return {"n": n, "percent": round(observed * 100, 1), "kappa": round(kappa, 2)}
