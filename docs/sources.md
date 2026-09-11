# Sources

Research and product references this project builds on. One line each on what is used from it.

## Memory extraction and reflection

- **Reflexion** (Shinn et al., 2023). Agents write verbal self-reflections after failures and reread them on the next attempt. Origin of the reflect-then-retry loop.
- **ExpeL** (Zhao et al., 2023), [arXiv:2308.10144](https://arxiv.org/abs/2308.10144). Extracts cross-task insights from success/failure pairs and edits an insight list with ADD / UPVOTE / DOWNVOTE / EDIT.
- **ReasoningBank** (Google, 2025), [arXiv:2509.25140](https://arxiv.org/abs/2509.25140). Distills "generalizable reasoning strategies" from successes and failures instead of storing raw trajectories. Assumes raw history is not enough, which is the assumption this lab tests.
- **Mem0** (2025), [arXiv:2504.19413](https://arxiv.org/abs/2504.19413). Production chat memory: extracts salient facts, then decides ADD / UPDATE / DELETE / NOOP against existing memories.
- **LangMem memory types** ([LangChain docs](https://docs.langchain.com/oss/python/concepts/memory)). Episodic, semantic and procedural memory. Basis for the note classification scheme.

## Evaluating memory in chat assistants

- **PrefEval** (ICLR 2025), [arXiv:2502.09597](https://arxiv.org/abs/2502.09597). Explicit vs implicit user preferences; zero-shot preference following falls below 10% at 10 turns for most models.
- **LongMemEval** (ICLR 2025), [arXiv:2410.10813](https://arxiv.org/abs/2410.10813). Five memory abilities including knowledge updates and abstention.
- **MEMPROBE** (2026), [arXiv:2606.24595](https://arxiv.org/abs/2606.24595). Task completion saturates even without memory, while recovery of the user's hidden state stays around 0.6. A task must actually need memory.
- **MemSyco-Bench** (2026), [arXiv:2607.01071](https://arxiv.org/abs/2607.01071). Retrieved memories can lower accuracy; most errors happen after the right memory was retrieved.

## Attribution

- **PAST-Bench** (2026), [arXiv:2608.04003](https://arxiv.org/abs/2608.04003). Matched on/off persistence episodes; agents with the same headline gain differ in whether the gain follows the intended memory pathway.

## Product context

- **ChatGPT "Dreaming"** (OpenAI, June 4 2026). Background rewriting of stale memories. [Coverage](https://www.resultsense.com/news/2026-06-05-openai-chatgpt-dreaming-memory/).
- **Gemini Spark** (Google I/O, May 2026). Always-on personal agent with Gmail and OpenTable integrations. [TechCrunch](https://techcrunch.com/2026/05/19/google-introduces-gemini-spark-a-24-7-agentic-assistant-with-gmail-integration/).

## To verify before citing

- Rakuten's reported 97% reduction in first-pass errors.
- claude-mem star count.
