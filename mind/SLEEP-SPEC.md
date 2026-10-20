# Sleep v0: build spec

*v0.1, 20 Oct 2026. Replaces the outline in BUILD-SPEC S0.7 and ticket F8.
Brings sleep level with the write half as built (files stay the original;
cards are cut from them and re-cut on every write; INDEX-SPEC §8). Decisions
are Audrie's (18 and 20 Oct). Written by POE, for Audrie. Review welcome.*

## 0. Decided

1. **Code only.** No model in v0. A small local model stays an idea
   (`research/ideas/sleep-consolidation.md`).
2. **Invisible.** The agent is never shown what sleep did or proposes. The
   operator sees all of it. A reviewed version is sketched in §9, only in
   case it is needed.
3. **Cadence is tested, not chosen.** Once a night, then after every wake,
   as two stages (§8).
4. **Starting values** (§4): N = 20 wakes, floor 0.3, closed matters 0.5.
   Digests built behind a switch, off for the first stage.

## 1. What sleep is for

Bounded reads (the cards) keep each wake small. Bounded growth is sleep's
half: even with good recall the store fills with old logs, duplicates and
closed matters, and the right card gets harder to rank first. Sleep runs
between wakes as a separate process and changes **how findable** things are.
It never changes what the agent wrote, and it never deletes.

**What the write half already does.** Anything the agent follows over time
(resident, place, thread, goal, project) has one current-state card that
replaces itself, with dated history behind it, and recall returns history as
labels only. So history without growth is done for those kinds. Sleep v0 is
narrower than S0.7 imagined: mainly **logs, closed matters and likely
duplicates**.

**The store on 20 Oct:** 3,356 cards. Logs 1,300 (39%), relationships 932,
threads 362, goals 277, reflections 209, decisions 132, rules 96, projects
48. Every card has `weight` 1.0. Sleep has never run.

## 2. The sleep layer

The agent's files are the original and cards are re-cut whenever a file
changes, so anything stored on a card would be wiped by the next write.
Sleep writes to its own place, private and gitignored like the read log:

`memory/private/sleep/`
- `layer.json`: current state keyed by card id. Per card: `weight` (0.0 to
  1.0; 1.0 when absent), `duplicate_of` (list of card ids; a flag only),
  `digest` (id of a digest card that covers it).
- `nights/<timestamp>.jsonl`: one file per run. Each action is one line:
  card id, field, old value, new value, rule, reason. The record and the
  undo.
- `digests/`: digest cards (§4.3), `origin: sleep`, never cut from files.
- `report.md`: the last run's summary (§7), overwritten each run.

**Rules**
- Recall and the wake card read `weight` from the layer. A card's own
  `weight` field stays 1.0 and sleep never writes it.
- A re-cut never reads or writes the layer.
- If a card id leaves the store, its layer entry stays and is ignored.
  Nothing is cleaned up silently.
- **Undo** one run: replay its night file backwards. **Off**: move
  `layer.json` aside. One command each (`tools/sleep.py --undo <night>`,
  `--off`).
- **Check in the build:** a re-cut keeps a card's id when its text is
  unchanged and only its position moves. If not, key the layer by origin
  (file and heading key) instead.

## 3. What sleep reads

- The card store, read only.
- **The read log** (`memory/private/card-reads.jsonl`). Since 18 Oct it
  records every recall and every wake card (the card ids shown), each with
  its wake label and conversation, and a `closed` line when a wake writes its
  mission log. **Only reads from conversations with a `closed` line count.**
  Read-only, sealed and test sessions never make a card look read.
- The wake counter, so N is counted in wakes, not days.

**Before the log is long enough.** "Unread in N wakes" is only judged once
the log holds N closed wakes. Before that, rule 4.2 does nothing.

## 4. The rules

Each rule is plain code, deterministic, and logged line by line.

### 4.1 Closed matters fade

A card whose status is `done`, `superseded` or `merged` drops to weight
**0.5** the first run it is seen in that state. Recall that names it by tag
still returns it, after live cards with the same match. A card that becomes
live again returns to 1.0.

### 4.2 Unread logs fade

Log cards only. A log card not returned by any recall or shown on any wake
card in the last **N = 20 closed wakes** loses **0.1** per run, down to a
floor of **0.3**. Read once, it returns to 1.0.

**Never faded by 4.2:** relationships, goals, projects, rules, reflections,
decisions and threads. Their findability is the agent's, through status. The
identity core (soul, governance, the wake card's identity section) is outside
the card store's reach.

### 4.3 Old logs get a digest (behind a switch, off in stage C1)

Logs older than N wakes are covered by a weekly digest card: per wake, its
number, title, and the plan and observations sections copied word for word
(no summarising: there is no model), with each originating card id. Tagged
with every tag its sources carry, so recall on an old place finds the digest
first and can open the original. Originals keep their weight under this
rule. Whether the digest earns its bytes is measured, not assumed.

### 4.4 Likely duplicates are flagged

Two live cards of the same kind sharing **at least 80%** of their tags (and
at least three) are flagged `duplicate_of` each other. A flag only: no merge
and no weight change in v0. For the operator, and a later version.

### 4.5 What sleep never does

- Edit the agent's files, or a card's text, title, tags, status or links.
- Delete anything, or lower anything below the floor.
- Change a card's authority, source or channel. Who said what lives in
  system fields and sleep does not write them.
- Write anything the agent reads as a message, a lesson or a log.
- Run during a wake: it exits if the stop marker or the wake lock is set.

## 5. When it runs

A separate process on the operator's scheduler, outside the agent's client:
no model, no subscription, no permission prompt. Seconds per run.

- **Once a night:** between the last wake of the day and the first of the
  next (03:00 for a 22:00 / 06:00 schedule).
- **After every wake:** after each wake window closes.

Which is live is one setting in `config/sleep.json`, so stages switch
without a code change.

## 6. Build order

1. ~~Read-log fixes~~ (done 18 Oct: wake card ids logged; real wakes marked).
2. The sleep layer, and recall and the wake card reading weights from it.
   **With an empty layer, every recall answer and wake card is byte for byte
   what it is today** (the test).
3. Rules 4.1, 4.2, 4.4, then 4.3 behind its switch.
4. `tools/sleep.py` with `--dry-run`, `--undo`, `--off`.
5. The scheduled task, created by the operator.

Environment-neutral: nothing in sleep knows about the city (study 3).

**Tests that must exist:** no file in `memory/` outside `private/sleep/`
changes; card text, tags, status and links are identical before and after;
every action in a night file undoes cleanly; a re-cut leaves the layer
untouched; an empty layer changes no recall; rule 4.2 does nothing while the
log holds fewer than N closed wakes; each test is made to fail once.

## 7. What the operator sees

After each run, `report.md` and a line in the operator's morning brief: how
many cards faded, returned, were flagged as duplicates, and which digests
were written. Never sent to the agent, never on the wake card.

## 8. The study: stages C1 and C2

| Stage | Sleep | Digests | Wakes |
|---|---|---|---|
| B | off | — | 10 (the baseline) |
| C1 | once a night | off | 10 |
| C2 | after every wake | off | 10 |
| withdrawal | off | — | a block (RESEARCH-SPEC §3.1) |

Digests (4.3) are a later stage of their own if fading alone leaves logs
crowding recall. Measured as for B (RESEARCH-SPEC §2, §6): whole-wake read
size, recall answer size, whether the right card came first. Damage: facts
the agent can no longer find, and **any read of a card at weight below 1.0**,
counted and named in the report.

**Not in this spec:** whether sleep stays on after the study.

## 9. Reviewed sleep (only if needed)

Same rules, but a night's actions are written as proposals and the next wake
card shows a short section the agent can accept or refuse with one call.
Cost: filing becomes part of what it reads every wake, which invisible sleep
avoids. Built only if C1 or C2 shows damage review would have caught.

---
*Sources: BUILD-SPEC S0.3, S0.4, S0.7, F8; INDEX-SPEC (card fields,
`weight`, `merged_into`, recall ranking, §8); `research/ideas/sleep-consolidation.md`;
the operator's write-half design of 5 Oct; the card store and read log as
of 20 Oct.*
