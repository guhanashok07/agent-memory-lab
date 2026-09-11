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
