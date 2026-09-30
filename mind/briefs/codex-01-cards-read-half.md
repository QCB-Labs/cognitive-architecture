# Codex brief 01: memory cards, read half (R1–R4)

*Paste this whole file into Codex. Written by POE for Audrie, 2026-09-30.*

---

Hi Codex. You are building the first part of a memory system for an AI agent.
Follow these steps **in order**. Do exactly what every step says. If a step
can't be done as written, **stop and report**. Don't work around it.

## Step 1. Read these files first (don't change them)

You start in the `agent-template` folder. Paths below are relative to it.

1. `..\cognitive-architecture\mind\INDEX-SPEC.md`
   — **this is the spec you are building.** Read all of it. You will build
   §2, §3, §4 and §5 only.
2. `..\cognitive-architecture\mind\BUILD-SPEC.md`
   — read only the section "Stage 0 — Foundation", for background.

## Step 2. Set up the branch

Work in the `agent-template` folder (the template repository). Every path in
this brief is relative to it. Its sibling folders are
`..\cognitive-architecture` (the specs) and `..\sputnik` (the agent).

Run:

```
git status
git switch main
git switch -c stage0/cards-read-half
```

If `git status` shows any changes before you start, **stop and report**. Don't
touch them.

## Step 3. Protect private data (do this before anything else)

1. Add this line to `.gitignore`: `fixtures/private/`
2. Run `git check-ignore fixtures/private/test.txt`. It must print the path.
   If it doesn't, stop and report.
3. Copy the agent's real memory into the private fixture:
   copy everything in
   `..\sputnik\memory`
   to `fixtures\private\sputnik-memory\` in this repo.
4. Run `git status`. **Nothing under `fixtures/private/` may appear.** If it
   does, stop and report.

This data is private. Never commit it, never copy it into a tracked file,
never paste its contents into a test that is tracked.

## Step 4. Rules for the whole job

- **Do not commit.** Leave every change uncommitted on the branch.
- **Do not change the agent's words.** Migration cuts text into cards. It
  never rewrites, shortens, summarises or cleans text.
- **Do not change** `GEMINI.md`, `STANDING-ORDERS.md`, or any file in the
  agent's memory folders. You only add new code and tests.
- **Your own code.** You may reuse code from this repository. Copy nothing
  from other projects.
- **Use the logical names** from `naming.json` (`lessons`, `open_threads`,
  `continuity`, `goals`, `journal`, `residents`, `city_rules`). Don't hardcode
  file names.
- **No city-specific code.** City tag patterns go in a config file (spec
  §4.1), not in Python.
- **Every check must fail once.** For each test you write, make it fail on
  purpose once (break the input), see it fail, then fix the input. Note this
  in your report.
- Put new code in a new module, `tools/cards.py`. Put tests in
  `tests/test_cards.py`. Don't restructure existing files.
- Run the full test suite at the end: `python -m pytest -q`. Existing tests
  must still pass.

## Step 5. Build ticket R1 — card store

Spec §2 and §3.
- `cards.jsonl`, append-only. Each write appends one full JSON line.
- The system sets: `id`, `tags`, `created_at`, `updated_at`, `wake`,
  `source`, `channel`, `weight`, `origin`. If a caller supplies any of them,
  refuse with a clear error.
- `index.json` is derived and can be rebuilt from `cards.jsonl` with one
  function call.

**Tests that must exist:**
1. Supplying a system field is refused.
2. Delete `index.json`, rebuild, get the same result.
3. After any number of writes, every earlier line of `cards.jsonl` is
   byte-for-byte unchanged.

## Step 6. Build ticket R2 — tag extractor

Spec §4.
- Patterns are read from a config file. Ship two:
  - `tag-patterns.generic.json` (wake numbers, dates, kind)
  - `tag-patterns.city.json` (residents, places, continents, notes, things,
    posts, kind IDs — see the table in §4.1)
- Ambiguous `#123` with no context becomes `ref:123`. Don't guess.
- Same text in, same tags out, every time.

**Tag test set:** pick at least 30 real lines from
`fixtures/private/sputnik-memory/` and write, for each, the tags it should
get. Keep this test set **inside `fixtures/private/`** (it contains real
text). Also write a small made-up test set in `tests/` for the tracked tests.

## Step 7. Build ticket R3 — migration

Spec §5.1 and §5.2.
- Cut each logical file into cards exactly as the table in §5.1 says.
- Propose `rule` or `reflection` for each lesson (§5.2). Write the proposals
  to `kind-review.md`. Every lesson card gets status `recheck` until
  confirmed.
- If any file doesn't fit its cutting rule, **stop and report with three
  examples.** Don't invent a new rule.

Run the migration on:
1. a small made-up fixture in `tests/fixtures/` (tracked), and
2. the private fixture (output stays in `fixtures/private/`).

## Step 8. Build ticket R4 — round trip

Spec §5.3. This is the most important test.
- Generate each original file back from the cards.
- Compare with the original. They must be identical, except for whitespace
  at the end of lines.
- Run it on both fixtures.
- If even one character differs, **R4 fails.** Report the file, the line and
  the difference.

**Stop after R4.** Don't start R5 or anything else.

## Step 9. Final checks

Run and include the output in your report:

```
python -m pytest -q
git status
git diff --stat
git check-ignore fixtures/private/test.txt
```

## Step 10. Write this report at the end

Reply with exactly these sections:

```
## Report: Codex brief 01 (R1–R4)

Branch: <branch name>
Committed anything: yes / no   (must be no)

### Tickets
R1 card store:      done / partial / not done — <one line>
R2 tag extractor:   done / partial / not done — <one line>
R3 migration:       done / partial / not done — <one line>
R4 round trip:      PASS / FAIL — <files checked, any differences>

### Numbers (private fixture)
Cards created, by kind: <kind: count, ...>
Lessons proposed as rule / reflection: <n> / <n>
Tag test set: <passed>/<total>

### Fail-once log
<each test, and how you made it fail once>

### Stopped or reported
<anything you couldn't build as written, with examples — or "none">

### Files changed
<git diff --stat output>

### Test suite
<pytest summary line>

### Private data check
git check-ignore output: <output>
Anything under fixtures/private/ in git status: yes / no   (must be no)

### Handoff
Did:          <one line>
Next action:  <one line>
Blocked on:   <who or what, or none>
New dates:    none
Needs Audrie: <review / decision / no>
```
