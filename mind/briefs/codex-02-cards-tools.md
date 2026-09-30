# Codex brief 02: memory cards — fixes, recall, wake card, market/Square

*Paste this whole file into Codex. Written by POE for Audrie, 2026-09-30.
Work repo: **`dev\agent-template`**, branch **`stage0/cards-read-half`**.*

---

Hi Codex. This continues brief 01 (R1–R4, commit `06febfd`, which you
built). Follow the steps **in order**. Do exactly what every step says. If a
step can't be done as written, **stop and report**. Don't work around it.

## Paths

`%USERPROFILE%` is the Windows user folder. Resolve it first
(`echo $env:USERPROFILE` in PowerShell) and use the full paths.

| Name | Full path | Access |
|---|---|---|
| WORK | `%USERPROFILE%\dev\agent-template` | read and write; **the only place you write** |
| SPECS | `%USERPROFILE%\Documents\World Sim\08 Agent testing\cognitive-architecture` | read only |
| AGENT_REPO | `%USERPROFILE%\Documents\World Sim\08 Agent testing\sputnik` | read only; copy from it, never write to it |

If any path doesn't exist, stop and report before Step 1.

## Step 1. Read (don't change)

1. `SPECS\mind\INDEX-SPEC.md` — **the spec, now v0.2.** Read all of it.
   Changes since brief 01 are marked "(v0.2)".
2. `SPECS\mind\briefs\codex-01-cards-read-half.md` — for context only.
3. In WORK: `tools\cards.py`, `tests\test_cards.py`, `tools\harness_mcp.py`,
   `tools\market_mcp.py`, `tools\square_mcp.py`, `naming.json`.

## Step 2. Check the branch

In WORK run:

```
git status
git switch stage0/cards-read-half
git log --oneline -1
```

The final line must read `06febfd`. The working tree must be clean. If not,
stop and report.

## Step 3. Rules for the whole job

- **Do not commit and do not push.** Only if Audrie tells you to in this
  chat, in her own message.
- **Write only inside WORK.** Never write to SPECS or AGENT_REPO.
- **Never change the agent's words.** Cards hold text exactly as written.
- **Don't edit** `GEMINI.md`, `STANDING-ORDERS.md` or any agent memory file
  in WORK's `records\` folder. New tools are added; no agent is told to use
  them yet.
- **No city names in Python.** City patterns stay in `config\`.
- **Every new test fails once on purpose first.** Log how.
- **Private data stays in `fixtures\private\`** (gitignored). Tracked tests
  use made-up fixtures only.
- Run the whole suite at the end: `python -m pytest -q`. All must pass.

## Step 4. Rebuild the private fixture (repo-shaped)

Brief 01 copied only Sputnik's `memory\` folder, so goals were missed.

1. Delete `fixtures\private\sputnik-memory\`, `fixtures\private\migration-output\`
   and `fixtures\private\roundtrip\` (all inside WORK). Check each path is
   under `WORK\fixtures\private\` before deleting.
2. Create `fixtures\private\sputnik\` and copy into it, from AGENT_REPO:
   `goals.md`, `SOUL.md`, `GOVERNANCE.md`, and the whole `memory\` folder.
   **Copy bytes exactly** (keep line endings): use `Copy-Item`, not a text
   rewrite.
3. Replace `fixtures\private\sputnik-naming.json` so its paths are relative
   to `fixtures\private\sputnik\` (the repo root), with `"memory": "memory"`
   and `goals` → `goals.md`.
4. Run `git status`. Nothing under `fixtures/private/` may appear.

## Step 5. Part A — fixes to brief 01 (INDEX-SPEC v0.2)

**A1. Goals from the repo root.** Migration reads each logical file from
where the naming file puts it, relative to the repo root (§3, v0.2).
Test: the made-up fixture has a goals file at its root and it becomes
`goal` cards.

**A2. Continuity cut on bullets.** §5.1 v0.2 row: one `decision` card per
top-level bullet; a heading (and text before its first bullet) goes with
the first bullet's card. Test on a made-up file with two sections and five
bullets → five cards, round trip exact.

**A3. Byte-exact round trip.** §5.3 v0.2: views regenerate **byte for
byte**, including CRLF/LF and a missing final newline. Store what's needed
(for example each file's line ending) so this works. Tests: one CRLF file
and one LF file with no final newline, both byte-identical after the round
trip. Compare bytes, not lines.

**A4. No-ID dossiers.** §5.1: a dossier with no resident ID becomes a
`relationship` card with tag `name:<handle>`, status `recheck`, listed in a
migration report file. Migration does not stop. Test with a made-up
dossier whose ID is `—`.

**A5. Resident tags are city IDs only.** §4.2 v0.2: `resident:` never holds
a Square or market number. Add patterns so Square citizen numbers become
`square:<n>` and market merchant numbers `market:<n>` where the text says
so. Test: a line naming a Square citizen number doesn't produce `resident:`.

Then run the migration and round trip on the new private fixture. Report
card counts by kind, how many `decision` cards continuity gave, and whether
the round trip is byte-identical for every file.

## Step 6. Part B — new tools (INDEX-SPEC §5.4, §6, §7)

Put tool code in `tools\cards.py` and expose tools from
`tools\harness_mcp.py` using the template's naming layer (see how other
tools get their names from `naming.json`). Cards for the template agent live
in `{memory}\cards\`.

**R5. Re-cut on write (§5.4).** After each existing file-writing harness
tool succeeds (for lessons, open threads, continuity, goals, journal and
resident dossiers), re-cut that one file into cards:
- An entry whose text is unchanged keeps its card and ID.
- A changed entry gets a new version of its card (same ID, new line in
  `cards.jsonl`).
- A new entry gets a new card.
- An entry that disappeared from the file: its card gets status `done` with
  reason `removed from source file`. Never delete the card.
- **The file stays the source.** If re-cutting fails, the file write still
  stands and the error is logged; don't undo the agent's write.

Tests: edit one entry in a file → exactly one card changes and every other
ID is the same; remove an entry → that card is `done`, still readable.

**R6. `recall` and `read_card` (§7).**
- `recall(tags, text=None, kinds=None, limit=10)` — ranking: matching tags,
  then weight, then newest. Returns cards plus what was searched, how many
  matched, how many were left out.
- Budget in a config file (proposed 4,000 tokens; tokens = characters ÷ 4).
  **Over budget is refused, not cut:** return the count and ask for a
  narrower query.
- Every recall appends to `{memory}\cards\reads.jsonl`. `cards.jsonl` stays
  byte-identical after any read.
- `read_card(id, history=False)`.

Tests: over budget refused; a recall leaves `cards.jsonl` unchanged; ranking
order.

**R7. `read_wake_card(here_tags=[])` (§6).** Five sections, always in this
order, "none" when empty:
1. Who I am — identity and governance files, whole, never trimmed.
2. What I was doing — the newest handover card if any (none exist yet), else
   the last section of the newest `log` card; plus `live` goals.
3. What I owe — `live` commitments (none yet: "none").
4. What needs checking — cards with status `recheck`.
5. What's here — `live` threads and relationships whose tags match
   `here_tags`.

Budgets in config: 3,000 / 2,000 / 2,000 / 4,000 tokens for sections 2–5.
Never cut a card in half: show the top cards that fit and say how many more
there are and how to recall them.

**Run it on the private fixture** with `here_tags` for one real place from
Sputnik's newest mission log. Report each section's size in tokens and the
total, and save the output to `fixtures\private\wake-card-sample.md`.

Section 4 note: brief 01 marked 108 lesson cards `recheck`. Report how many
show and how many are left out; don't change the statuses.

## Step 7. Part C — market and Square catch-up (BUILD-SPEC F11)

In a read-only test wake, `browse_shelves` returned 43 KB and
`read_square_profile` 20 KB. Add, **without changing existing defaults**:

1. `market_mcp.browse_shelves(..., since_id=None, brief=False)`:
   `since_id` returns only listings with an id greater than it; `brief=True`
   cuts each description to 200 characters and adds `"truncated": true`.
2. `square_mcp.read_new_posts(..., since_id=None)`: only posts with an id
   greater than it.
3. A new `square_mcp.read_square_quotas()`: only handle, citizen number and
   today's quotas from the same `/api/me` call.

The agent will store the last ids with the existing harness last-seen tool;
you don't change the protocol. Tests with faked HTTP responses (follow how
the existing market/Square tests fake them). If there are no existing tests
to copy, stop and report.

**Stop after Step 7.** Don't port anything to Sputnik. Don't start the
write half.

## Step 8. Final checks

Run and paste the output:

```
python -m pytest -q
git status
git diff --stat
git check-ignore fixtures/private/test.txt
```

Also run `git -C "<AGENT_REPO>" status --short` and
`git -C "<SPECS>" status --short` and paste both, to show you wrote nothing
there.

## Step 9. Report

Reply with exactly this:

```
## Report: Codex brief 02

Branch: stage0/cards-read-half   (starting commit: 06febfd)
Committed anything: yes / no
Pushed anything: yes / no

### Part A
A1 goals:            done / partial / not done — <one line>
A2 continuity cut:   done / partial / not done — <decision cards now: n>
A3 byte-exact:       PASS / FAIL — <files checked, differences>
A4 no-ID dossiers:   done / partial / not done
A5 resident tags:    done / partial / not done

### Private fixture after Part A
Cards by kind: <kind: count, ...>
Round trip byte-identical: <n>/<n> files

### Part B
R5 re-cut on write:  done / partial / not done — <one line>
R6 recall/read_card: done / partial / not done — <one line>
R7 wake card:        done / partial / not done
Wake card on private fixture (tokens): s1 <n> | s2 <n> | s3 <n> | s4 <n> | s5 <n> | total s2–s5 <n>
Section 4: shown <n>, left out <n>

### Part C
browse_shelves since_id/brief: done / partial / not done
read_new_posts since_id:       done / partial / not done
read_square_quotas:            done / partial / not done

### Fail-once log
<each new test and how it failed once>

### Stopped or reported
<anything you couldn't build as written, with examples — or "none">

### Files changed
<git diff --stat>

### Test suite
<pytest summary line>

### Private data and other repos
git check-ignore: <output>
fixtures/private/ in git status: yes / no
AGENT_REPO status: <output, must be empty>
SPECS status: <output, must be empty>

### Handoff
Did:          <one line>
Next action:  <one line>
Blocked on:   <who or what, or none>
New dates:    none
Needs Audrie: <review / decision / no>
```
