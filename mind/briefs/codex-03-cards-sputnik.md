# Codex brief 03: memory cards — port to Sputnik (R8)

*Paste this whole file into Codex. Written by POE for Audrie, 2026-09-30.
Work repo: **`dev\sputnik`**, new branch **`stage0/cards-sputnik`**.*

---

Hi Codex. Briefs 01 and 02 built memory cards in the template
(`dev\agent-template`, branch `stage0/cards-read-half`, commit `6a3859d`).
This brief brings the same thing to **Sputnik**, a live agent. Follow the
steps **in order**. Do exactly what every step says. If a step can't be done
as written, **stop and report**. Don't work around it.

## Paths

`%USERPROFILE%` is the Windows user folder. Resolve it first
(`echo $env:USERPROFILE` in PowerShell) and use the full paths.

| Name | Full path | Access |
|---|---|---|
| WORK | `%USERPROFILE%\dev\sputnik` | read and write; **the only place you write** |
| TEMPLATE | `%USERPROFILE%\dev\agent-template` | read only (branch `stage0/cards-read-half`) |
| SPECS | `%USERPROFILE%\Documents\World Sim\08 Agent testing\cognitive-architecture` | read only |

If any path doesn't exist, stop and report before Step 1.

**Never touch** the vault copy of Sputnik
(`%USERPROFILE%\Documents\World Sim\08 Agent testing\sputnik`). WORK is a
separate clone made for this job.

## Step 1. Read (don't change)

1. `SPECS\mind\INDEX-SPEC.md` (v0.2), especially §5.4, §6, §7, §9 and the R8
   row in §10.
2. In TEMPLATE: `tools\cards.py`, `config\cards.json`,
   `config\tag-patterns.generic.json`, `config\tag-patterns.city.json`, and
   how `tools\harness_mcp.py` exposes `recall`, `read_card`,
   `read_wake_card` and calls the re-cut after writes. Read the market and
   Square changes in `tools\market_mcp.py` and `tools\square_mcp.py`.
3. In WORK: `tools\harness_mcp.py`, `tools\market_mcp.py`,
   `tools\square_mcp.py`, `tools\release.py`, `.gitignore`, `GEMINI.md`.

## Step 2. Branch

In WORK run:

```
git status
git switch main
git log --oneline -1
git switch -c stage0/cards-sputnik
```

`git status` must be clean and the log must show `50c233c`. If not, stop
and report.

## Step 3. Rules for the whole job

- **Do not commit and do not push.** Only if Audrie tells you to in this
  chat, in her own message.
- **Write only inside WORK.**
- **Never change the agent's words.** Migration cuts his files into cards;
  the text stays exactly as he wrote it.
- **Don't edit** `GEMINI.md`, `GOVERNANCE.md`, `soul.md`, `goals.md` or any
  file in `memory\` except the new `memory\cards\` folder. The protocol
  change is a **proposal file** (Step 8), never an edit.
- **No silence or restraint lines** in the proposal. Nothing that makes it
  harder for him to speak or answer. "People first" still opens Act.
- **Every new test fails once on purpose first.** Log how.
- **Reuse, don't rewrite.** Copy `tools\cards.py` and the three config files
  from TEMPLATE. Change them only where Sputnik differs, and list every
  difference in your report.
- Sputnik's harness uses **fixed file names** (no `naming.json` layer). Don't
  add the template's naming system. Use the small card naming file in Step 4.
- Run his whole suite at the end: `python -m pytest -q`. All must pass
  (570 before you start).

## Step 4. Copy the card code and config

1. Copy from TEMPLATE into WORK, byte for byte: `tools\cards.py`,
   `config\cards.json`, `config\tag-patterns.generic.json`,
   `config\tag-patterns.city.json`. Create `config\` if missing.
2. Create `config\card-naming.json` with Sputnik's real paths (relative to
   WORK):

```json
{
  "dirs": {"memory": "memory"},
  "paths": {
    "identity": "soul.md",
    "governance": "GOVERNANCE.md",
    "goals": "goals.md",
    "lessons": "memory/lessons.md",
    "city_rules": "memory/city-rules.md",
    "open_threads": "memory/open-threads.md",
    "continuity": "memory/continuity.md",
    "journal": "memory/mission_log",
    "residents": "memory/residents"
  },
  "indexes": {"residents": "memory/residents/index.md"}
}
```

3. Copy the card tests from TEMPLATE's `tests\test_cards.py` into WORK's
   `tests\test_cards.py`, using made-up fixtures only (copy TEMPLATE's
   `tests\fixtures\cards\`). No Sputnik text in any test.

## Step 5. Where the cards live, and the privacy boundary

**Read this carefully.** Sputnik's harness treats **anything gitignored as
private** (`tools\release.py` derives the private set from `.gitignore`),
and private files are gated. If the cards were gitignored, his own wake card
would be locked away from him.

So:
- `memory\cards\cards.jsonl` and `memory\cards\index.json` are **tracked**
  (not gitignored). They hold the same text as his tracked memory files.
- The read log goes to `memory\private\card-reads.jsonl` (already private),
  **not** `memory\cards\reads.jsonl`. The agent never reads it; it's research
  data.
- `memory\cards\kind-review.md` and the migration report are tracked.

Check with `tools\release.py` (or its tests) that `memory/cards/cards.jsonl`
is **not** in the private set and `memory/private/card-reads.jsonl` **is**.
If the result is different, stop and report.

## Step 6. Migrate his real memory

1. Run the migration on WORK itself (repo root = WORK, naming =
   `config\card-naming.json`, patterns = `config\tag-patterns.city.json`,
   output = `memory\`).
2. Generate the views into a temporary folder **outside the repo** and
   compare **bytes** with every source file. Must be identical.
3. Run `git status`. The only new tracked paths must be under
   `memory\cards\`, `config\`, `tools\cards.py` and `tests\`. No existing
   memory file may show as modified. If one does, stop and report.

Report: card counts by kind, files checked, byte differences.

## Step 7. Wire the tools into his harness (R5, R6, R7)

In WORK's `tools\harness_mcp.py`:

**Add three tools** (same behaviour as TEMPLATE): `recall`, `read_card`,
`read_wake_card(here_tags=[])`. Budgets from `config\cards.json`. The wake
card returns its text **once** (sections carry sizes and counts only, as in
TEMPLATE `6a3859d`).

**Re-cut after these existing writers succeed** (R5), each for its own
file. Don't change what they do or what they return:

| Writer | File |
|---|---|
| `append_lesson` | `memory/lessons.md` |
| `propose_city_rule` | `memory/city-rules.md` |
| `update_open_threads` | `memory/open-threads.md` |
| `update_continuity` | `memory/continuity.md` |
| `update_goals` | `goals.md` |
| `write_mission_log`, `file_unrecorded` | the new mission log file |
| `upsert_resident` | that dossier and `memory/residents/index.md` |

If a re-cut fails, the agent's write still stands; log the error to
`memory\private\card-errors.log` and return the writer's normal result.

**If `memory\cards\cards.jsonl` doesn't exist** when a card tool or re-cut
runs, run the migration first (so a fresh clone works).

**Old read tools stay.** `read_soul`, `read_lessons`,
`read_open_threads` and the rest remain installed, unchanged.

Tests (with made-up fixtures): each writer above triggers exactly one
re-cut of its file; a failing re-cut doesn't undo the write; the three new
tools respond; `cards.jsonl` is unchanged after `recall` and
`read_wake_card`.

## Step 8. Market and Square (F11)

Port the TEMPLATE changes to WORK's `tools\market_mcp.py` and
`tools\square_mcp.py`: `browse_shelves(since_id, brief)`,
`read_new_posts(since_id)`, `read_square_quotas()`. Defaults unchanged.
Port their tests.

## Step 9. The protocol proposal (don't apply it)

Write `proposals\gemini-read-steps.md` in WORK. It contains:

1. **A unified diff against `GEMINI.md`**, proposing:
   - Pre-flight steps 2–7 (soul, governance, goals, continuity, lessons,
     recent mission log) become **one** call: `harness.read_wake_card()`.
   - After `city.me` (step 9), a `harness.recall(tags=[...])` for the
     current place and anyone present, in place of reading whole files.
   - Step 15 (open threads): `harness.recall` by tag instead of
     `harness.read_open_threads`.
   - Step 17: `market.browse_shelves(sort="new", since_id=<last seen>,
     brief=True)`, `square.read_new_posts(since_id=<last seen>)`,
     `square.read_square_quotas()` in place of the profile; the last ids
     stored with the existing `harness.update_last_seen` under feeds
     `market` and `square`.
   - A line saying the old read tools are still there if the wake card is
     missing something.
2. **Three city calls that failed in a test wake on 30 Sept**, for Audrie
   to fix separately (don't change them in the diff): an unsupported
   `after_change_id` argument, a `browse` view that doesn't exist, and an
   unsupported `query` argument. Name the GEMINI.md lines that use them.
3. A short **plain-English summary** of what changes for Sputnik at wake.

The diff must not remove or weaken anything about people, speaking,
answering, authority, spending or publishing. If it would, stop and report.

## Step 10. Measure

Run `read_wake_card(here_tags=["place:1212"])` on WORK and report each
section's tokens (characters ÷ 4) and the total. Save the text to
`%USERPROFILE%\dev\sputnik-wake-card-sample.md` (outside the repo).

**Stop after Step 10.** Don't start the write half.

## Step 11. Final checks

Run and paste:

```
python -m pytest -q
git status
git diff --stat
```

## Step 12. Report

Reply with exactly this:

```
## Report: Codex brief 03 (port to Sputnik)

Model: <exact model name and setting>
Branch: stage0/cards-sputnik   (from 50c233c)
Committed anything: yes / no
Pushed anything: yes / no

### Copied from TEMPLATE, and what differs
<files; every change from TEMPLATE and why>

### Privacy boundary (Step 5)
cards.jsonl private?: yes / no   (must be no)
card-reads.jsonl private?: yes / no   (must be yes)

### Migration of his real memory
Cards by kind: <kind: count, ...>
Byte round trip: <n>/<n> files identical
Existing memory files modified: yes / no   (must be no)

### Tools
recall / read_card / read_wake_card:  done / partial / not done
Re-cut after writers:                 <each writer: done / not done>
Market/Square F11:                    done / partial / not done

### Wake card on his memory (tokens)
s1 <n> | s2 <n> | s3 <n> | s4 <n> | s5 <n> | total <n>

### Proposal
proposals/gemini-read-steps.md written: yes / no
Removes or weakens anything about people or speaking: yes / no   (must be no)

### Fail-once log
<each new test and how it failed once>

### Stopped or reported
<anything, with examples — or "none">

### Files changed
<git diff --stat, plus new files>

### Test suite
<pytest summary line>

### Handoff
Did:          <one line>
Next action:  <one line>
Blocked on:   <who or what, or none>
New dates:    none
Needs Audrie: <review / decision / no>
```
