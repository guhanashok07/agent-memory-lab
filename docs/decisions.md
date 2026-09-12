# Decision log

Each entry: what was decided, the options considered, and why. Newest last.

## 001. Task: a writing assistant (2026-09-10)

**Decided:** The assistant drafts email replies for one scripted user across a series of sessions. The user has hidden style rules. Drafts are graded by mechanical text checks.

**Considered:** coding in a synthetic repo; a simulated tool/API world; an existing benchmark (tau-bench); spec-conformance transforms; a recommendation concierge; a support bot with house policies.

**Why:** Writing is one of the most common things people use AI for, and one where users still report disappointment. Mechanical grading means no human judgment decides pass or fail. The concierge (Gemini Spark / OpenTable style) is the planned extension; it needs implicit preferences (revealed only through rejections) or it measures fact recall rather than learning.

## 002. Scripted user, not a simulated one (2026-09-10)

**Decided:** The user's messages are fixed scripts. Only the reaction to a rule violation branches.

**Why:** A second model playing the user adds noise and doubles local runtime. Cost: conversations are less natural.

## 003. Note classification: type and test (2026-09-10)

**Decided:** Every memory note gets (a) a type label, episodic / semantic / procedural, and (b) a transfer test: the note alone is given to a fresh assistant on an unseen email, and it passes if the draft now obeys a hidden rule.

**Considered:** wording only; type only; test only.

**Why:** Wording and usefulness can disagree ("Never use exclamation marks in the recruiter email" looks like a rule but is tied to one email). Having both shows how often rule-shaped notes actually work.

## 004. Feedback: mixed explicit and implicit (2026-09-10)

**Decided:** Some rules are stated by the user ("too long"), others only shown through the user's edits.

**Why:** Explicit-only lets the assistant copy the comment. Implicit-only may yield almost nothing from a small model. Mixed is realistic and allows a directional comparison.

## 005. Two reflection prompts (2026-09-10)

**Decided:** A failure-framed prompt ("what went wrong?") and a rule-framed prompt ("what should you do differently next time?"), about 20 sessions each.

**Why:** The hypothesis claims the prompt framing causes descriptive notes. With one prompt, only the what can be reported, not the why.

## 006. Portfolio integration (2026-09-10)

**Decided:** The page lives at guhanashok.com/work/agent-memory, following the site's /work/<slug> convention. The AI Evals Suite placeholder and its URL are removed outright. The portfolio reads a versioned JSON results file published from this repo.

## 007. Models (2026-09-10)

**Decided:** The assistant is `qwen3:8b` (Ollama digest `500a1f067a9f`). The note labeler is `gemma3:12b` (digest `f4031aab637d`), from a different model family so it is not grading its own writing.

**Considered:** `qwen3:14b` (better writing, about 2x slower); `llama3.1:8b` (older, widely used).

**Why:** Fast enough for about 40 sessions plus transfer tests on a laptop, and weak enough that extraction failures show up. Limitation for the writeup: a larger model may extract differently.

## 008. Rules come from generic office style (2026-09-10)

**Decided:** The user's five hidden rules are neutral office-email conventions anyone can check at a glance.

**Considered:** Guhan's own voice rules; a mix.

## 009. Memory policy: the assistant curates (2026-09-10)

**Decided:** After each session the assistant proposes notes, then decides ADD / UPDATE / DELETE / NOOP against its existing memory (Mem0-style). Both layers are logged: the raw reflection output, and the curated memory after edits. Question 1 classifies the raw reflection output; the curated memory is reported alongside.

**Considered:** keep everything and reread everything; keep the newest 10.

**Why:** Closest to shipped products. Logging the raw layer separately keeps curation from muddying the extraction measurement.

## 010. Repository (2026-09-10)

**Decided:** Public at github.com/guhanashok07/agent-memory-lab. `main` requires a pull request and blocks force-pushes, so it only changes through reviewed merges. MIT licence.

## 011. The five hidden rules (2026-09-10)

| # | Rule | How the user reveals it | Check |
|---|---|---|---|
| 1 | Under 120 words | Stated: "Too long." | word count |
| 2 | Lead with the answer | Stated: "Get to the point." | the email's known answer word appears in the first sentence |
| 3 | No exclamation marks | Shown: user's edit removes them | no `!` |
| 4 | No filler openers ("I hope this finds you well") | Shown: user's edit deletes the line | banned-phrase list |
| 5 | Sign off "Best, G" | Shown: user's edit replaces the sign-off | last line matches |

## 012. Reflection prompts (2026-09-10)

- **Failure-framed:** "Review this session. What went wrong, and what should you remember?"
- **Rule-framed:** "Review this session. Write the rules you should follow in every future email to this user."

The rule-framed prompt will produce notes that look rule-shaped by construction. The transfer test (003) is what shows whether they work.

## 013. Thinking mode off (2026-09-10)

**Decided:** Qwen3 runs with thinking disabled.

**Why:** Like a chat product's fast mode, and about 3x faster. The reflection step is then the only place the model reasons about a session, which is the thing being measured. Hidden reasoning would blur what the notes contain.

## 014. Paired seeds at temperature 0.7 (2026-09-10)

**Decided:** Temperature 0.7 with a fixed seed per session. Both prompt arms see the same emails, in the same order, with the same seeds.

**Considered:** temperature 0.

**Why:** Keeps natural variation while making the prompt the only difference between arms. Every run is reproducible from its config.

## 015. The pilot changed the rules (2026-09-11)

**What happened:** A no-memory pilot on the 20 session emails showed three of the original five rules passing 95 to 100% by default: qwen3:8b writes very short replies (median 14 words). A rule the assistant already follows cannot show learning, the same trap MEMPROBE reports.

**First fix tried:** a warmer persona ("warm, friendly, complete emails, the way a helpful assistant would"), matching how product assistants default to padded emails. Kept, because it mirrors real products. It revived "no exclamation marks" (40%) but pushed "Best, G" to 80% and left the other two at 100%.

**Decided:** Rules v2, chosen from candidates measured on the pilot drafts:

| # | Rule | Revealed | No-memory pass rate |
|---|---|---|---|
| 1 | Under 25 words | Stated: "Too long." | 20% |
| 2 | Lead with the answer | Stated: "Get to the point." | 70% |
| 3 | No exclamation marks | Shown (edit) | 40% |
| 4 | No filler openers or closers ("Let me know if you need anything") | Shown (edit) | 35% |
| 5 | No contractions | Shown (edit) | 20% |

Dropped: under 120 words, filler openers only, sign off "Best, G".

## 016. Results reach the portfolio as a copied file (2026-09-11)

**Decided:** A results file is copied into the portfolio repo through a pull request. The page imports it at build time.

**Considered:** fetching a tagged release URL at build time; fetching in the browser.

**Why:** The site then never depends on GitHub, at build or at view time, which is the independence constraint taken literally. The pull request doubles as a review gate: new numbers go live only after someone reads them. Cost: one small portfolio PR per results version.

## 017. Labeler prompt v2 (2026-09-11)

**What happened:** The v1 labeler (gemma3:12b) labelled plain instructions such as "Keep responses concise to match the recipient's style" as episodic, and called 97 of 123 rule-prompt notes episodic.

**Decided:** Define each type by its grammatical form, add contrast examples and a tie-break (instruction plus description counts as procedural), re-label all notes, and adopt v2 only if it agrees with Guhan's 30 blind hand labels at Cohen's kappa of 0.6 or higher. v1 labels stay in the git history.

## 018. A noise floor for the transfer test (2026-09-11)

**What happened:** A spot check found 2 of 10 irrelevant notes ("G uses a MacBook") passing the transfer test, both on the no-contractions rule. Any note in the prompt nudges the model's style.

**Decided:** 30 irrelevant control notes run through the identical test. Their transfer rate is published as the noise floor, and every note-type rate is read against it.

**Considered:** a stricter threshold or more held-out emails. Fewer false positives, but also fewer true ones, and a 45-minute rerun.

## 019. Labeler v2 validated on 10 blind human labels (2026-09-12)

**What happened:** Guhan labelled 10 notes blind, before seeing any model label. Agreement with labeler v2 was 8 of 10, Cohen's kappa 0.64, clearing the 0.6 bar set in 017.

**Both disagreements ran the same way:** gemma called an imperative episodic ("Don't add extra context unless it's relevant") where Guhan called it procedural. So the published procedural share is, if anything, an undercount.

**Caveat for the writeup:** n is 10, not 30. Kappa on 10 items is a weak estimate.
