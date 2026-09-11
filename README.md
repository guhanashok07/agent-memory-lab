# Agent Memory Lab

A controlled test of agent memory. When an AI assistant reflects on a session and writes notes for next time, what does it actually write down, and do those notes help?

**Status:** in design. The harness does not exist yet. See [docs/decisions.md](docs/decisions.md) for every design decision so far and why it was made, and [docs/sources.md](docs/sources.md) for the research it builds on.

## Questions

1. **Extraction.** Does the assistant write transferable rules or descriptions of what happened? (In progress.)
2. **Attribution.** Is any improvement caused by the memory, or by extra context or easier tasks? (Planned.)
3. **Decay.** When a rule changes, how long does the old lesson survive? (Planned.)

## Running it

Setup instructions (three commands, including Ollama) will land here with the first working harness.

Everything runs locally through [Ollama](https://ollama.com). There is no API spend and there are no secrets.
