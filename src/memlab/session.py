"""Question 1 sessions: draft, react, reflect, curate. Each arm keeps its own memory."""

import re
from pathlib import Path

from . import ollama, prompts
from .rules import check
from .store import append_jsonl
from .user import react


def _clean(text: str) -> str:
    return re.sub(r"<think>.*?</think>", "", text, flags=re.S).strip()


def draft(model: dict, memory: list[str], email: dict, seed: int, log) -> str:
    call = ollama.chat(
        model,
        [
            {"role": "system", "content": prompts.draft_system(memory)},
            {"role": "user", "content": prompts.draft_task(email)},
        ],
        seed=seed,
    )
    log("draft", call)
    return _clean(call["content"])


def apply_ops(memory: list[dict], ops: list[dict], next_id: int):
    """Apply the assistant's curation. Invalid operations (unknown id, empty text)
    are rejected and logged rather than guessed at."""
    memory = [dict(m) for m in memory]
    applied, rejected = [], []
    for op in ops:
        kind, mid = op.get("op"), op.get("id")
        text = (op.get("text") or "").strip()
        ids = {m["id"] for m in memory}
        if kind == "ADD" and text:
            memory.append({"id": next_id, "text": text})
            next_id += 1
        elif kind == "UPDATE" and mid in ids and text:
            for m in memory:
                if m["id"] == mid:
                    m["text"] = text
        elif kind == "DELETE" and mid in ids:
            memory = [m for m in memory if m["id"] != mid]
        else:
            rejected.append(op)
            continue
        applied.append(op)
    return memory, next_id, applied, rejected


def run_sessions(config: dict, emails: list[dict], run: Path) -> None:
    model = config["assistant"]
    session_emails = [e for e in emails if e["split"] == "session"][: config["sessions"]]

    for arm in config["arms"]:
        memory: list[dict] = []
        next_id = 1
        for i, email in enumerate(session_emails):
            # Paired seeds: session i uses the same seed in every arm, so the prompt
            # framing is the only designed difference between arms (decision 014).
            seed = config["session_seed"] + i

            def log(stage, call, _arm=arm, _i=i):
                append_jsonl(run / "calls.jsonl", {"stage": stage, "arm": _arm, "session": _i, **call})

            memory_before = memory
            text = draft(model, [m["text"] for m in memory], email, seed, log)
            grade = check(text, email["answers"])
            reaction = react(text, grade)

            reflected, call = ollama.chat_json(
                model,
                [
                    {"role": "system", "content": prompts.MEMORY_SYSTEM},
                    {"role": "user", "content": prompts.reflect_task(email, text, reaction, arm)},
                ],
                seed=seed,
                schema=prompts.NOTES_SCHEMA,
            )
            log("reflect", call)
            notes = [n.strip() for n in reflected["notes"] if n.strip()]

            curated, call = ollama.chat_json(
                model,
                [
                    {"role": "system", "content": prompts.MEMORY_SYSTEM},
                    {"role": "user", "content": prompts.curate_task(memory, notes)},
                ],
                seed=seed,
                schema=prompts.OPS_SCHEMA,
            )
            log("curate", call)
            memory, next_id, applied, rejected = apply_ops(memory, curated["operations"], next_id)

            append_jsonl(
                run / "sessions.jsonl",
                {
                    "arm": arm,
                    "session": i,
                    "email_id": email["id"],
                    "seed": seed,
                    "memory_before": memory_before,
                    "draft": text,
                    "grade": grade,
                    "reaction": reaction,
                    "notes": notes,
                    "operations_applied": applied,
                    "operations_rejected": rejected,
                    "memory_after": memory,
                },
            )
            print(f"{arm} session {i + 1}/{len(session_emails)}: {sum(grade.values())}/5 rules, {len(notes)} notes, memory {len(memory)}")


def run_pilot(config: dict, emails: list[dict], run: Path) -> dict[str, float]:
    """Drafts with empty memory on the session emails, same seeds as the real run.
    Tells us how often each rule is followed with no memory at all."""
    model = config["assistant"]
    session_emails = [e for e in emails if e["split"] == "session"][: config["sessions"]]
    totals: dict[str, int] = {}
    for i, email in enumerate(session_emails):
        def log(stage, call, _i=i):
            append_jsonl(run / "pilot_calls.jsonl", {"stage": stage, "session": _i, **call})

        text = draft(model, [], email, config["session_seed"] + i, log)
        grade = check(text, email["answers"])
        append_jsonl(run / "pilot.jsonl", {"session": i, "email_id": email["id"], "draft": text, "grade": grade})
        for rule, ok in grade.items():
            totals[rule] = totals.get(rule, 0) + ok
    return {rule: n / len(session_emails) for rule, n in totals.items()}
