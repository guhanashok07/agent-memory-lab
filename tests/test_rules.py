from memlab.rules import check, first_sentence
from memlab.user import edit, react

GOOD = "Hi Priya,\n\nThursday at 3pm works. I will send an invite.\n\nBest,\nG"

BAD = """Hi Priya,

I hope this email finds you well! Thanks so much for reaching out about the sync.

Thursday at 3pm works for me. I'll send an invite, and we won't need long.

Let me know if you need anything else!

Best,
G"""


def test_good_draft_passes_everything():
    assert all(check(GOOD, ["Thursday"]).values())


def test_bad_draft_fails_every_rule():
    assert not any(check(BAD, ["Thursday"]).values())


def test_greeting_with_a_sentence_counts_as_body():
    assert first_sentence("Hi Priya, Thursday works.\n\nBest,\nG") == "Hi Priya, Thursday works."


def test_answer_must_be_a_whole_word():
    assert not check("Hi,\n\nThe 219 figure stands.", ["19"])["answer_first"]


def test_possessives_are_not_contractions():
    assert check("Friday's review is set. The team's slides are done.", ["Friday"])["no_contractions"]


def test_user_edit_fixes_only_the_shown_rules():
    edited = edit(BAD)
    result = check(edited, ["Thursday"])
    assert result["no_exclamation"] and result["no_filler"] and result["no_contractions"]
    assert "I will send an invite, and we will not need long." in edited


def test_stated_rules_get_a_comment_and_no_edit():
    draft = "Hi,\n\nSure. Thursday works."
    assert react(draft, check(draft, ["Thursday"])) == "Get to the point."


def test_clean_draft_is_accepted():
    assert react(GOOD, check(GOOD, ["Thursday"])) == "Looks good. Sending it as is."
