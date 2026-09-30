# Codex briefs: how to write one

Every brief starts, right after its greeting, with a **Paths** block. It
names each folder once, as a full Windows path. Later steps use the names
(`WORK`, `SPECS`, `AGENT_MEMORY`), never `..\` paths. If a folder moves,
change the block and nothing else.

```
## Paths

| Name | Full path | Access |
|---|---|---|
| WORK | %USERPROFILE%\dev\agent-template | read and write; the only place to write |
| SPECS | %USERPROFILE%\Documents\World Sim\08 Agent testing\cognitive-architecture | read only |
| AGENT_MEMORY | %USERPROFILE%\Documents\World Sim\08 Agent testing\sputnik\memory | read only; copy from it, never write to it |

If any path here doesn't exist, stop and report before Step 1.
```

Rules that came out of brief 01 (2026-09-30):

- Codex writes only under `%USERPROFILE%\dev\`. Its patch tool can't
  write inside the Obsidian vault (reparse point).
- Say which repo is `WORK` in the first line of the brief. Brief 01 was run
  once in the wrong repo.
- If the branch may already exist, say "switch to it, or create it if
  missing".
