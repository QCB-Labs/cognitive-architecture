# mind

The build specs, written alongside the research spec in `research/`.

- `INDEX-SPEC.md`: Stage 0. The agent's memory files are cut into small
  labelled cards; a wake reads one bounded wake card and recalls the rest.
  The code lives in the agent's harness, not here. Both halves, read
  and write (§8), are built and in use.
- `LINKS-SPEC.md`: stage C. Recall and the resident and thread readers
  also list cards that share an entity tag with what they returned.
  Decided 25 Nov 2026; built in the agent's harness, off until stage C
  starts.
- `SLEEP-SPEC.md`: stage D. A code-only pass between wakes that weighs
  cards. Specified (v0.3), not built.
- `BUILD-SPEC.md`: Stage 0 in outline, then the mind server (stage E). The
  server is not built yet and is reviewed before any code.
