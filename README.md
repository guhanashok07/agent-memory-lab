# Agent Memory Lab

A controlled test of agent memory. When an AI assistant reflects on a session and writes notes for next time, what does it actually write down, and do those notes help?

**Status:** in design. The harness does not exist yet. See [docs/decisions.md](docs/decisions.md) for every design decision so far and why it was made, and [docs/sources.md](docs/sources.md) for the research it builds on.

## Questions

1. **Extraction.** Does the assistant write transferable rules or descriptions of what happened? (In progress.)
2. **Attribution.** Is any improvement caused by the memory, or by extra context or easier tasks? (Planned.)
3. **Decay.** When a rule changes, how long does the old lesson survive? (Planned.)

## Running it

Needs [Ollama](https://ollama.com/download) (running) and [uv](https://docs.astral.sh/uv/).

```bash
ollama pull qwen3:8b && ollama pull gemma3:12b
uv sync
uv run memlab all
```

That writes raw logs to `runs/<config name>/` and the published results to `results/<config name>.json`. Stages can also run one at a time: `pilot`, `sessions`, `transfer`, `label`, `handlabel` (interactive), `export`. The harness refuses to run if your local model digests differ from the ones pinned in `configs/`.

Everything runs locally through [Ollama](https://ollama.com). There is no API spend and there are no secrets.
