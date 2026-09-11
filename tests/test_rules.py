from memlab.rules import check, first_sentence
from memlab.user import edit, react

GOOD = """Hi Priya,

Thursday at 3pm works. I'll send an invite.

Best,
G"""

BAD = """Hi Priya,

I hope this email finds you well! Thanks so much for reaching out about the sync.

Thursday at 3pm works for me. I'll send an invite.

Best regards,
[Your Name]"""


def test_good_draft_passes_everything():
    assert all(check(GOOD, ["Thursday"]).values())


def test_bad_draft_fails_the_right_rules():
    result = check(BAD, ["Thursday"])
    assert result == {
        "length": True,
        "answer_first": False,
        "no_exclamation": False,
        "no_filler_opener": False,
        "sign_off": False,
    }


def test_greeting_with_a_sentence_counts_as_body():
    assert first_sentence("Hi Priya, Thursday works.\n\nBest,\nG") == "Hi Priya, Thursday works."


def test_answer_must_be_a_whole_word():
    assert not check("Hi,\n\nThe 219 figure stands.\n\nBest,\nG", ["19"])["answer_first"]


def test_length_limit():
    long = "Hi,\n\nThursday. " + "word " * 130 + "\n\nBest,\nG"
    assert not check(long, ["Thursday"])["length"]


def test_user_edit_fixes_only_the_shown_rules():
    result = check(edit(BAD), ["Thursday"])
    assert result["no_exclamation"] and result["no_filler_opener"] and result["sign_off"]


def test_stated_rules_get_a_comment_and_no_edit():
    draft = "Hi,\n\nSure. Thursday works.\n\nBest,\nG"
    reply = react(draft, check(draft, ["Thursday"]))
    assert reply == "Get to the point."


def test_clean_draft_is_accepted():
    assert react(GOOD, check(GOOD, ["Thursday"])) == "Looks good. Sending it as is."
