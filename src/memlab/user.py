"""The scripted user.

The user never improvises. Stated rules get a fixed comment. Shown rules are only
revealed by the user's own edit of the draft, with no explanation (decision 004).
"""

import re

from .rules import FILLER

STATED = {
    "length": "Too long.",
    "answer_first": "Get to the point.",
}
SHOWN = ("no_exclamation", "no_filler_opener", "sign_off")

# Short closing lines only, so "Thanks again for the update." is not mistaken for one.
CLOSING = re.compile(
    r"^(best|best regards|kind regards|warm regards|regards|thanks|thank you|many thanks"
    r"|cheers|sincerely|all the best|talk soon)\b",
    re.I,
)


def _strip_filler(text: str) -> str:
    out = []
    for line in text.splitlines():
        parts = re.split(r"(?<=[.?!])\s+", line)
        kept = [p for p in parts if not FILLER.search(p)]
        if line.strip() and not kept:
            continue
        out.append(" ".join(kept))
    return "\n".join(out)


def _strip_sign_off(text: str) -> str:
    lines = text.rstrip().splitlines()
    for i in range(len(lines) - 1, max(len(lines) - 5, -1), -1):
        line = lines[i].strip()
        if CLOSING.match(line) and len(line.split()) <= 4:
            return "\n".join(lines[:i]).rstrip()
    return text.rstrip()


def edit(draft: str) -> str:
    """What the user actually sends: the draft with every shown rule fixed."""
    text = draft.replace("!", ".")
    text = _strip_filler(text)
    text = _strip_sign_off(text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return f"{text}\n\nBest,\nG"


def react(draft: str, result: dict[str, bool]) -> str:
    if all(result.values()):
        return "Looks good. Sending it as is."
    parts = [comment for rule, comment in STATED.items() if not result[rule]]
    if any(not result[rule] for rule in SHOWN):
        parts.append("Here's the version I actually sent:\n\n" + edit(draft))
    return "\n\n".join(parts)
