# Cognitive Architecture

A persistent mind for LLM agents, held outside the model, and the experiment
that tests it.

| Folder | Holds |
|---|---|
| [`spec/`](spec/) | The Cognitive Architecture specification and its verification record |
| [`mind/`](mind/) | The build specs. `INDEX-SPEC.md`: memory cut into cards, a bounded wake card and recall; built and in use. `LINKS-SPEC.md`: links between cards (stage C); built, off until C starts. `SLEEP-SPEC.md`: sleep (stage D); not built. `BUILD-SPEC.md`: the mind server, an MCP server that holds the agent's ledgers and validates every write (stage E); not built. |
| [`research/`](research/) | The research spec, protocols, metric scripts and published results |

The baseline agent is
[`agent-harness-template`](https://github.com/QCB-Labs/agent-harness-template).
Each experimental run names the template commit it was built on.

## Where the study stands

Study 1 runs on one agent living in the [1F3D9](https://1f3d9.com) city, one
change per stage. Stage B, the baseline (cards and bounded reads), closed on
30 October 2026: [results](research/stage-B-results.md). The agent's model
changed on 17 November 2026, so a fresh ten-wake baseline, B′, is run on the
new model before stage C, and C is compared against both. Next are stage C
(links between cards), D (sleep) and E (the mind server).

## Licence

- `mind/`: [PolyForm Noncommercial 1.0.0](LICENSE).
- `spec/` and `research/`: [CC BY-NC 4.0](spec/LICENSE) (and `research/LICENSE`).

Free for research, study, hobby and other non-commercial use. Commercial use
needs permission. Contributions: see [CONTRIBUTING.md](CONTRIBUTING.md).

## Hooks

See [hooks/README.md](hooks/README.md) before committing.
