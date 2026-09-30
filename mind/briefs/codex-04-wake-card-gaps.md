# Codex brief 04: three wake card sections, and the proposal to match

*Paste this whole file into Codex. Written by POE for Audrie, 2026-09-30.
Work repos: **`dev\agent-template`** (branch `stage0/cards-read-half`) first,
then **`dev\sputnik`** (branch `stage0/cards-sputnik`).*

---

Hi Codex. Review of brief 03 found three things Sputnik reads at every wake
today that the wake card would silently drop. Add them. Follow the steps in
order; if a step can't be done as written, stop and report.

## Paths

`%USERPROFILE%` is the Windows user folder; resolve it first.

| Name | Full path | Access |
|---|---|---|
| TEMPLATE | `%USERPROFILE%\dev\agent-template` | read and write |
| WORK | `%USERPROFILE%\dev\sputnik` | read and write |
| SPECS | `%USERPROFILE%\Documents\World Sim\08 Agent testing\cognitive-architecture` | read only |

Pytest's own default temp folder is allowed. Nothing else outside TEMPLATE
and WORK.

## Rules

- **Do not commit and do not push**, unless Audrie says so in this chat.
- Never change the agent's words. Don't edit `GEMINI.md` or any memory file
  (except regenerated `memory\cards\` in WORK, Step 4).
- Every new test fails once on purpose first. Log how.
- The proposal must not remove or weaken anything about people, speaking,
  answering, authority, spending or publishing.

## Step 1. Check both branches

TEMPLATE: `git status` clean, `git log --oneline -1` shows `6a3859d`.
WORK: `git status` clean, `git log --oneline -1` shows `103c947`.
If not, stop and report.

## Step 2. The three gaps (why)

1. **Threads with people who aren't present.** Today every living thread is
   read at every wake. The proposal only recalls threads tagged with the
   current place or people present, and "What I owe" stays empty until
   commitment cards exist. He could forget to answer someone elsewhere.
2. **Durable decisions** (`continuity`) aren't in the wake card at all.
3. **Rules** (short lessons and city rules) aren't in the wake card unless
   they're `recheck` or match a tag.

## Step 3. Add three sections to `read_wake_card` (TEMPLATE `tools\cards.py`)

The card becomes eight sections, in this order:

1. Who I am *(unchanged)*
2. What I was doing *(unchanged)*
3. What I owe *(unchanged)*
4. **Open threads (index)** — one line per `live` thread card:
   `- <card id>: <title> [<resident and place tags>]`. Titles only, never
   the thread body. Newest `updated_at` first. Budget `thread_index`, 2,000.
   The line after the list says: "Recall a thread with read_card(<id>) or
   recall(tags=[...])."
5. **Decisions** — `live` `decision` cards, full text, file order. Budget
   `decisions`, 5,000.
6. **Rules** — `live` `rule` cards, full text, newest first. Cards with
   status `recheck` don't appear here (they're in "What needs checking").
   Budget `rules`, 3,000.
7. What needs checking *(was 4, unchanged)*
8. What's here *(was 5, unchanged)*

Same rules as the other sections: never cut a card in half; say how many
were left out and how to recall them; the text goes out once. Add the three
budgets to `config\cards.json`.

Tests (made-up fixture): eight sections in this order; the thread index
shows titles and no body text; a `recheck` rule is not in Rules; each new
section respects its budget.

Run the full TEMPLATE suite. All must pass.

## Step 4. Bring it to WORK

Copy the changed `tools\cards.py`, `config\cards.json` and the new tests
from TEMPLATE into WORK. Keep WORK's one difference (the read log path
`memory/private/card-reads.jsonl`). Run WORK's full suite. All must pass.

Measure `read_wake_card(here_tags=["place:1212"])` on WORK: tokens per
section (characters ÷ 4) and the total. Save the text to
`%USERPROFILE%\dev\scratch-brief03\sputnik-wake-card-sample-04.md`.

## Step 5. Update the proposal (WORK `proposals\gemini-read-steps.md`)

1. Steps 2–7 text: name all eight sections, and say the thread index lists
   every open thread so none is forgotten.
2. Step 15: first look at the thread index in the wake card; `recall` or
   `read_card` a thread in full when it's relevant or someone is waiting —
   not only threads at the current place.
3. Add one line to Step 15: "Before saying something doesn't exist or never
   happened, `recall` it first and say where you looked (Article 6)."
4. Keep everything else in the proposal as it is.

## Step 6. Report

```
## Report: Codex brief 04

Model: <exact model and setting>
Committed anything: yes / no
Pushed anything: yes / no

TEMPLATE: three sections added: done / partial / not done
TEMPLATE suite: <pytest summary>
WORK: ported: done / partial / not done
WORK suite: <pytest summary>

Wake card on Sputnik's memory (tokens):
who <n> | doing <n> | owe <n> | thread index <n> | decisions <n> | rules <n> | checking <n> | here <n> | total <n>
Threads listed: <n> of <n> live   Rules shown: <n> of <n> live

Proposal updated: yes / no
Removes or weakens anything about people or speaking: yes / no  (must be no)

Fail-once log:
<each new test and how it failed once>

Stopped or reported: <or "none">

Files changed:
<git diff --stat for each repo>

Handoff
Did:          <one line>
Next action:  <one line>
Blocked on:   <or none>
New dates:    none
Needs Audrie: <review / decision / no>
```
