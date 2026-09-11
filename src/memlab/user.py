"""The scripted user.

The user never improvises. Stated rules get a fixed comment. Shown rules are only
revealed by the user's own edit of the draft, with no explanation (decision 004).
"""

import re

from .rules import CONTRACTION, FILLER

STATED = {
    "length": "Too long.",
    "answer_first": "Get to the point.",
}
SHOWN = ("no_exclamation", "no_filler", "no_contractions")

_SPECIAL = {"won't": "will not", "can't": "cannot", "shan't": "shall not", "let's": "let us"}
_SUFFIX = {"n't": " not", "'ll": " will", "'re": " are", "'m": " am", "'s": " is", "'ve": " have", "'d": " would"}


def _expand(match: re.Match) -> str:
    word = match.group(0).replace("’", "'")
    lower = word.lower()
    if lower in _SPECIAL:
        out = _SPECIAL[lower]
    else:
        suffix = "n't" if lower.endswith("n't") else lower[lower.index("'"):]
        out = word[: len(word) - len(suffix)] + _SUFFIX[suffix]
    return out[0].upper() + out[1:] if word[0].isupper() else out


def _strip_filler(text: str) -> str:
    out = []
    for line in text.splitlines():
        parts = re.split(r"(?<=[.?!])\s+", line)
        kept = [p for p in parts if not FILLER.search(p)]
        if line.strip() and not kept:
            continue
        out.append(" ".join(kept))
    return "\n".join(out)


def edit(draft: str) -> str:
    """What the user actually sends: the draft with every shown rule fixed."""
    text = draft.replace("!", ".")
    text = _strip_filler(text)
    text = CONTRACTION.sub(_expand, text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def react(draft: str, result: dict[str, bool]) -> str:
    if all(result.values()):
        return "Looks good. Sending it as is."
    parts = [comment for rule, comment in STATED.items() if not result[rule]]
    if any(not result[rule] for rule in SHOWN):
        parts.append("Here's the version I actually sent:\n\n" + edit(draft))
    return "\n\n".join(parts)
