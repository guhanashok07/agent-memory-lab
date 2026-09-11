"""Every prompt the harness sends, in one place, so the wording is auditable."""

DRAFT_SYSTEM = (
    "You are an email assistant working for one user, G. Each session, G shows you an "
    "email they received and what they want to say back. Write the reply for G to send. "
    "Write warm, friendly, complete emails, the way a helpful assistant would. "
    "Output only the email itself, with no subject line and no commentary."
)


def draft_system(memory: list[str]) -> str:
    if not memory:
        return DRAFT_SYSTEM
    notes = "\n".join(f"- {n}" for n in memory)
    return f"{DRAFT_SYSTEM}\n\nYour memory notes about G, from earlier sessions:\n{notes}"


def draft_task(email: dict) -> str:
    return (
        f"Email from {email['sender']}\nSubject: {email['subject']}\n\n{email['body']}\n\n"
        f"What I want to say: {email['intent']}\n\nDraft my reply."
    )


# Decision 012. Same length and structure; only the framing differs.
REFLECT = {
    "failure": "Review this session. What went wrong, and what should you remember?",
    "rule": "Review this session. Write the rules you should follow in every future email to this user.",
}

MEMORY_SYSTEM = "You are an email assistant maintaining your own memory about G, the user you work for."


def reflect_task(email: dict, draft: str, reaction: str, arm: str) -> str:
    return (
        f"Email G received, from {email['sender']}:\n{email['body']}\n\n"
        f"What G wanted to say: {email['intent']}\n\n"
        f"Your draft:\n{draft}\n\n"
        f"G's response:\n{reaction}\n\n"
        f"{REFLECT[arm]}\n\nReturn a list of notes, one idea per note."
    )


NOTES_SCHEMA = {
    "type": "object",
    "properties": {"notes": {"type": "array", "items": {"type": "string"}}},
    "required": ["notes"],
}


def curate_task(memory: list[dict], notes: list[str]) -> str:
    current = "\n".join(f"[{m['id']}] {m['text']}" for m in memory) or "(empty)"
    new = "\n".join(f"- {n}" for n in notes) or "(none)"
    return (
        f"Your memory right now:\n{current}\n\n"
        f"New notes from the latest session:\n{new}\n\n"
        "Update your memory. Return one operation per change: ADD with the text of a new "
        "memory, UPDATE with the id of an existing memory and its new text, or DELETE with "
        "the id of a memory that is wrong or no longer needed. Return an empty list if "
        "nothing should change."
    )


OPS_SCHEMA = {
    "type": "object",
    "properties": {
        "operations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "op": {"type": "string", "enum": ["ADD", "UPDATE", "DELETE"]},
                    "id": {"type": "integer"},
                    "text": {"type": "string"},
                },
                "required": ["op"],
            },
        }
    },
    "required": ["operations"],
}

# Examples are deliberately unrelated to the five hidden rules.
LABEL_SYSTEM = "You classify notes that an AI email assistant wrote for its own memory."

# v2 (decision 017). v1 labelled plain instructions like "Keep responses concise" as
# episodic, so v2 defines each type by its grammatical form and adds a tie-break.
LABEL_TASK = """Classify the note as exactly one type, by its form.

procedural: an instruction or guideline for writing future emails. Imperatives ("Use first names",
  "Be warm but brief") and "should" statements are procedural, even without "always", and even if
  they mention a reason or a person.
semantic: a general fact about G or G's preferences, stated as a fact rather than an instruction
  ("G prefers informal emails").
episodic: a description of one particular session: a specific draft, edit, email or person, usually
  in the past tense ("My reply to Priya was too formal", "The final version removed a sentence").

If a note mixes an instruction with a description, choose procedural.

Examples:
"Greet people by first name." -> procedural
"You should mention deadlines early." -> procedural
"G likes a relaxed tone." -> semantic
"The draft to Omar used a formal greeting and G changed it." -> episodic

Note: {note}"""

LABEL_SCHEMA = {
    "type": "object",
    "properties": {"type": {"type": "string", "enum": ["episodic", "semantic", "procedural"]}},
    "required": ["type"],
}
