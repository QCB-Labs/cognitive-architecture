# Cognitive Architecture

A persistent mind for LLM agents, held outside the model, and the experiment
that tests it.

| Folder | Holds |
|---|---|
| [`spec/`](spec/) | The Cognitive Architecture specification and its verification record |
| [`mind/`](mind/) | The mind server: an MCP server that holds the agent's ledgers and validates every write. Not built yet. |
| [`research/`](research/) | The research spec, protocols, metric scripts and published results |

The baseline agent is
[`agent-harness-template`](https://github.com/qualitycontrolbureau/agent-harness-template).
Each experimental run names the template commit it was built on.

## Licence

- `mind/`: [PolyForm Noncommercial 1.0.0](LICENSE).
- `spec/` and `research/`: [CC BY-NC 4.0](spec/LICENSE) (and `research/LICENSE`).

Free for research, study, hobby and other non-commercial use. Commercial use
needs permission. Contributions: see [CONTRIBUTING.md](CONTRIBUTING.md).

## Hooks

See [hooks/README.md](hooks/README.md) before committing.
