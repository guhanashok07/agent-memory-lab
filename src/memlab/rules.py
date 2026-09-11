"""The five hidden rules and their checks.

Every check is plain string logic, so pass or fail never depends on a model's
judgment. See docs/decisions.md, entry 011.
"""

import re

RULES = {
    "length": "Under 120 words",
    "answer_first": "Lead with the answer in the first sentence",
    "no_exclamation": "No exclamation marks",
    "no_filler_opener": "No filler openers",
    "sign_off": 'Sign off "Best, G"',
}

MAX_WORDS = 120

FILLER = re.compile(
    r"hope (this|my) (e-?mail|message|note) finds you"
    r"|hope you('| a)re (doing )?well"
    r"|hope all is well"
    r"|hope you('| a)re having"
    r"|hope you had"
    r"|trust (this|you)",
    re.I,
)

# A greeting line on its own: "Hi Priya," or "Hello!". A line that carries a full
# sentence after the name is body text, so it cannot end in a full stop or question.
GREETING = re.compile(r"^(hi|hello|hey|dear|good (morning|afternoon|evening))\b[^.?]{0,30}$", re.I)

SIGN_OFF = re.compile(r"Best,\s*\n?\s*G\s*$")


def word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9][\w'’.%-]*", text))


def _lines(text: str) -> list[str]:
    return [line.strip() for line in text.strip().splitlines() if line.strip()]


def first_sentence(text: str) -> str:
    lines = [line for line in _lines(text) if not line.lower().startswith("subject:")]
    if lines and GREETING.match(lines[0]):
        lines = lines[1:]
    body = " ".join(lines)
    return re.split(r"(?<=[.?!])\s+", body, maxsplit=1)[0] if body else ""


def contains_answer(sentence: str, answers: list[str]) -> bool:
    return any(re.search(rf"(?<!\w){re.escape(a)}(?!\w)", sentence, re.I) for a in answers)


def check(draft: str, answers: list[str]) -> dict[str, bool]:
    return {
        "length": word_count(draft) < MAX_WORDS,
        "answer_first": contains_answer(first_sentence(draft), answers),
        "no_exclamation": "!" not in draft,
        "no_filler_opener": not FILLER.search(draft),
        "sign_off": bool(SIGN_OFF.search(draft.strip())),
    }
