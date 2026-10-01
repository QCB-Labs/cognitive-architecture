# Codex brief 04b: order and budgets in the three new wake card sections

> **Not run by Codex.** POE did this work directly on 2026-10-01, at Audrie's
> word. Kept as the record of what the brief 04 review found.

*Paste this whole file into Codex, in the same chat as brief 04 if it is still
open. Written by POE for Audrie, 2026-10-01. Continues on the uncommitted
brief 04 changes in **`dev\agent-template`** (branch `stage0/cards-read-half`)
and **`dev\sputnik`** (branch `stage0/cards-sputnik`).*

---

Hi Codex. Brief 04 was built as written and both suites pass. The review
found that the brief itself was wrong on one point: it sorted threads and
rules by `updated_at`. On migrated cards `updated_at` is the time of the
migration, not the age of the memory, so the order came out backwards. Follow
the steps in order; if a step can't be done as written, stop and report.

## Paths

`%USERPROFILE%` is the Windows user folder; resolve it first.

| Name | Full path | Access |
|---|---|---|
| TEMPLATE | `%USERPROFILE%\dev\agent-template` | read and write |
| WORK | `%USERPROFILE%\dev\sputnik` | read and write |
| SPECS | `%USERPROFILE%\Documents\World Sim\08 Agent testing\cognitive-architecture` | read only |
| SCRATCH | `%USERPROFILE%\dev\scratch-brief03` | write only the one output named in Step 4 |

Pytest's own default temp folder is allowed. Nothing else outside TEMPLATE,
WORK and SCRATCH.

## Rules

- **Do not commit and do not push**, unless Audrie says so in this chat.
- Never change the agent's words. Don't edit `GEMINI.md` or any memory file.
- Every new or changed test fails once on purpose first, **by breaking the
  behaviour the test is about** (for example: reverse the sort and watch the
  order test fail). A missing input file is not a fail-once. Log how.
- The proposal must not remove or weaken anything about people, speaking,
  answering, authority, spending or publishing.

## Step 1. Check the starting state

TEMPLATE: on `stage0/cards-read-half`, last commit `6a3859d`, with the
uncommitted brief 04 changes (`config/cards.json`, `tests/test_cards.py`,
`tools/cards.py`, new `tests/test_wake_sections.py`).
WORK: on `stage0/cards-sputnik`, last commit `103c947`, with the uncommitted
brief 04 changes. If not, stop and report.

## Step 2. What the review found (why)

Measured on WORK's cards:

1. **Open threads (index) dropped the ten newest threads.** `thread-0001` to
   `thread-0006` and `thread-0008` to `thread-0011` were left out. Those are
   the most recent ones, including the place he is standing in. The source
   file lists newest first, so file order is the right order.
2. **The index did not fit.** All 47 lines need about 2,550 tokens; the
   budget was 2,000. The point of the index is that no open thread is
   forgotten.
3. **Rules came out in reverse file order.** The cards carry the source
   file's own headings ("Confirmed", "Proposed (unverified …)", "Retracted
   …"), so reversed, each heading sits over the wrong rules.
4. **Rules did not fit either.** All 39 live rule cards need about 3,500
   tokens; the budget was 3,000.

## Step 3. Fix `read_wake_card` (TEMPLATE `tools\cards.py`)

1. **Threads:** sort by `origin.file`, then `origin.order`, ascending (the
   same key Decisions already uses). Cards with no `origin` come first,
   newest `updated_at` first.
2. **Rules:** the same key and the same no-`origin` rule.
3. **Budgets** in `config\cards.json`: `thread_index` 3000, `rules` 4000.
   `decisions` stays 5000.
4. **Left-out threads are named.** When the index leaves entries out, the
   notice lists their card ids: `N more thread(s) not listed: thread-0001,
   thread-0002, … Read each with read_card(<id>).` The ids count towards the
   budget.
5. Nothing else in `read_wake_card` changes.

Tests (made-up fixture), in `tests\test_wake_sections.py`:

- threads come out in `origin` order even when `updated_at` runs the other
  way;
- rules the same;
- a card with no `origin` comes before the ones that have it;
- the left-out notice names every left-out thread id, and the section stays
  inside its budget.

Update the two existing order tests to match. Run the full TEMPLATE suite.
All must pass.

## Step 4. Bring it to WORK and measure

Copy the changed `tools\cards.py`, `config\cards.json` and
`tests\test_wake_sections.py` from TEMPLATE into WORK. Keep WORK's one
difference (the read log path `memory/private/card-reads.jsonl`). Run WORK's
full suite. All must pass.

Measure `read_wake_card(here_tags=["place:1212"])` on WORK: tokens per
section (characters ÷ 4) and the total. Save the text to
`%USERPROFILE%\dev\scratch-brief03\sputnik-wake-card-sample-04b.md`.

Check on the sample and report yes or no for each:

- the index lists all 47 live threads, `thread-0001` first;
- the Rules section shows all 39 live rules, and its headings appear in the
  same order as in `memory\city-rules.md`.

If either is no, stop and report; don't raise a budget yourself.

## Step 5. The proposal (WORK `proposals\gemini-read-steps.md`)

Update only the last section, "What changes at wake", so it names the thread
index, decisions and rules. Leave the diff block as it is.

## Report

```
## Report: Codex brief 04b
Model:
Committed anything: no / yes (why)
Pushed anything: no / yes (why)

TEMPLATE suite:
WORK suite:

Wake card on Sputnik's memory (tokens):
who | doing | owe | thread index | decisions | rules | checking | here | total
All 47 threads listed, thread-0001 first: yes / no
All 39 rules shown, headings in file order: yes / no

Fail-once log (what was broken, which test failed):

Stopped or reported:

Files changed:

Handoff
Did:
Next action:
Blocked on:
New dates:
Needs Audrie:
```
