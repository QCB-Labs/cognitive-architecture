# Sleep v0: build spec

*v0.2, 21 Oct 2026. Replaces v0.1 (20 Oct), the outline in BUILD-SPEC S0.7
and ticket F8. Brings sleep level with the write half as built (files stay
the original; cards are cut from them and re-cut on every write; INDEX-SPEC
§8). Decisions are Audrie's (18 and 20 Oct). Written by POE, for Audrie.
Review welcome. What changed from v0.1 and why: §10.*

## 0. Decided

1. **Code only.** No model in v0. A small local model stays an idea
   (`research/ideas/sleep-consolidation.md`).
2. **Invisible.** The agent is never shown what sleep did or proposes. The
   operator sees all of it. A reviewed version is sketched in §9, only in
   case it is needed.
3. **Cadence is tested, not chosen.** Once a night, then after every wake,
   as two stages (§8).
4. **Starting values** (§4): N = 20 closed wakes, floor 0.3, closed matters
   0.5. Digests built behind a switch, off for the first stage.

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
mainly about **logs**: on 21 Oct, 1,046 live log cards, every one with
`role: history`.

## 2. Where sleep can act: recall's history order

Recall puts every current card before every history card, then fills a
separate history share (`recall_history_bytes`, 6,000) from the history
matches. In v0.1 the history order was: tags matched, log number, date. It
never read weight, so **fading a log could change nothing he recalls**
(Astra, 21 Oct; checked by POE: 1,036 of 1,036 live logs were history).

**v0.2 adds one sort key.** The history order becomes: tags matched,
**weight**, log number, date. Weight comes from the sleep layer (§3); with
no layer every card keeps its own `weight` (1.0 on his cards), so **with
sleep off, every recall answer is byte for byte what it is today.** This is
the test that keeps stage B clean.

**What it does, measured** (21 Oct, a frozen copy of his cards and the 82
recalls logged since W202, read only): 70 of them reach history; with
rule 4.2 applied, the history part of **47 of the 70 would change**. So the
treatment has a real route to what he reads.

**With links (LINKS-SPEC, draft).** Recall's linked list is ranked by the same weight, so sleep moves rarely used cards down the list, never off it while its tag is shared. That is the way back that makes fading safe.

**What it does not do.** A faded log never moves ahead of, or behind, a
current card; it competes only with other history of the same tag match.
The wake card's newest log is chosen by log number and is never faded.

**The risk it brings.** Only 41 of 1,046 logs were read in the 18 wakes the
read log covers. Fading the unread ones puts the read ones first, which
makes them likelier to be read again: findability can feed on itself. This
is what the damage measure (§8) watches for.

## 3. The sleep layer

The agent's files are the original and cards are re-cut whenever a file
changes, so anything stored on a card would be wiped by the next write.
Sleep writes to its own place, private and gitignored like the read log:

`memory/private/sleep/`
- `layer.json`: current state keyed by card id. Per card: `weight` (0.0 to
  1.0), `duplicate_of` (list of card ids; a flag only), `digest` (id of a
  digest card that covers it). Plus `last_wake`: the newest closed wake the
  layer has counted.
- `nights/<timestamp>.jsonl`: one file per run. Each action is one line:
  card id, field, old value (or "absent"), new value, rule, reason. The
  record and the undo.
- `digests/`: digest cards (§5.3), `origin: sleep`, never cut from files.
- `report.md`: the last run's summary (§7), overwritten each run.

**Rules**
- Recall and the wake card **rank** by the layer's `weight` where an entry
  has one, and by the card's own `weight` otherwise. The weight is used for
  ordering only: the cards returned to the agent carry their own fields,
  unchanged, so nothing he receives shows sleep's values.
- Sleep never writes a card's own `weight`. A re-cut never reads or writes
  the layer.
- A card id that leaves the store keeps its layer entry, ignored. Nothing is
  cleaned up silently.
- **On and off** are one setting, `enabled` in `config/sleep.json`. Off
  means recall ignores the layer and sleep does nothing; the layer stays as
  it was, for the record. The scheduler can't switch it back on.
- **Undo** replays a night file backwards, restoring "absent" as absent.
  Only the newest night not yet undone can be undone, so nights unwind in
  order and a later night is never overwritten by an earlier one.
- **Writes are atomic**: the night file is written in full first, then the
  layer replaced in one move. A run that dies leaves the old layer and a
  night file marked incomplete, which the next run reports and does not
  apply.
- **Card ids.** The build checks that a re-cut keeps a card's id when its
  text is unchanged and only its position moves, across every cutter,
  including repeated headings. Where an id can move to different text (a
  known case: an entry removed and its neighbour edited in one pass, a
  strict xfail in his tests), the layer entry is dropped for that card and
  the drop is logged, rather than following the wrong text.

## 4. What sleep reads

- The card store, read only.
- **The read log** (`memory/private/card-reads.jsonl`). Since 21 Oct
  (Sputnik `ea533fd`) every event carries `session` (`wake`, or `sealed`
  while the operator's marker stands), the wake card logs every card it
  shows, `read_card` is logged, and a wake's `closed` line is written last,
  after its log is mailed and cut.
- **A read counts** when its `session` is `wake` and a `closed` line exists
  for the same wake label. Reads without `session` (before 21 Oct) count
  only for wakes W202 onward that have a `closed` line; earlier reads are
  ignored. Sealed reads never count.
- The wake counter, so N is counted in closed wakes, not days.

**Before the log is long enough.** Rule 4.2 does nothing until the log
holds N closed wakes. On 21 Oct it holds 18.

## 5. The rules

Each rule is plain code, deterministic, and logged line by line. Rules run
in the order below; where two rules set a card's weight, the **lower**
value stands, and the night file names both.

### 5.1 Unread logs fade (the main rule)

Log cards only. A log card **at least N closed wakes old** (created before
the Nth-newest closed wake) that was not returned by any recall, shown on
any wake card, or opened with `read_card` in the last **N = 20 closed
wakes** loses **0.1** for each closed wake counted since `last_wake`, down
to a floor of **0.3**. Read once, it returns to 1.0 at the next run.
A run with no new closed wake changes nothing, so a retried or doubled run
can't fade twice.

### 5.2 Closed matters fade

A card whose status is `done`, `superseded` or `merged` drops to **0.5**
the first run it is seen in that state; live again, it returns to 1.0.
Ordinary recall doesn't return these cards at all, so this only orders
`history=True` answers (finished projects and threads). Kept for
completeness; its effect is reported, not assumed.

### 5.3 Old logs get a digest (behind a switch, off in D1 and D2)

Logs older than N closed wakes are covered by a weekly digest card: per
wake, its number, title, and the plan and observations sections copied word
for word (no summarising: there is no model), with each originating card id.
Tagged with every tag its sources carry, so recall on an old place finds
the digest and can open the original. Originals keep their weight under
this rule. Whether a digest earns its bytes is a later stage of its own.

### 5.4 Likely duplicates are flagged

Two **live** cards of the same kind are flagged `duplicate_of` each other
when they share at least three tags and the shared tags are at least **80%
of the union** of their tags (Jaccard ≥ 0.8). A flag only: no merge, no
weight change in v0. A flag whose cards no longer meet the test is removed
at the next run, and the removal logged.

### 5.5 What sleep never does

- Edit the agent's files, or a card's text, title, tags, status or links.
- Delete anything, or lower a weight below the floor.
- Change a card's authority, source or channel. Who said what lives in
  system fields and sleep does not write them.
- Write anything the agent reads as a message, a lesson or a log.
- Run during a wake (§6).

## 6. When it runs

A separate process on the operator's scheduler, outside the agent's client:
no model, no subscription, no permission prompt. Seconds per run.

- **Once a night:** 03:00, between the 22:00 and 06:00 wakes.
- **After every wake:** at :45 in the hour of each wake (wakes fire at :12 and
  take about 10 to 25 minutes).

Which is live is `cadence` in `config/sleep.json`.

**Not during a wake.** Sleep takes the harness's cross-process stop lock,
the same one `write_mission_log` takes, for its whole run. It also exits,
changing nothing, if `STOP.md` stands, or if the read log's newest event is
a `wake` read less than 45 minutes old with no `closed` line for its wake.
That check can't see a wake that hasn't read anything yet, so the schedule
keeps sleep out of the wake window as well; the report says which guard,
if any, stopped a run.

## 7. What the operator sees

After each run, `report.md` and a line in the operator's morning brief: how
many cards faded, returned, were flagged as duplicates, which digests were
written, and which guard stopped a run. Never sent to the agent, never on
the wake card.

## 8. The study: stages D1 and D2

*Changed 21 Oct evening, accepted by Audrie: links become stage C (`mind/LINKS-SPEC.md`), so sleep is stage D and acts on the linked list.*

| Stage | Sleep | Digests | Wakes |
|---|---|---|---|
| B | off | — | 10 (the baseline) |
| C | off; links on | — | 10 |
| D1 | once a night | off | 10 |
| D2 | after every wake | off | 10 |
| withdrawal | off | — | a block (RESEARCH-SPEC §3.1) |

- **Each stage starts from an empty layer.** D2 does not inherit D1's
  weights, so cadence and accumulated exposure aren't mixed. The previous
  layer is kept aside for the record.
- **The read history is kept across stages**, so D1 doesn't spend its ten
  wakes below N. It covers W202 onward, the wakes with `closed` lines.
- **Rules don't change between D1 and D2.** A change after D1 would change
  the treatment as well as the cadence; it waits for the comparison to end,
  or is logged as a new stage.

**Measured** as for B (RESEARCH-SPEC §2, §6): whole-wake read size, recall
answer size, whether the right card came first. Plus, for each recall in a
C stage, **the counterfactual**: the same query on the same card snapshot
with the layer off, computed afterwards from the logged query, never by
recalling again. Changed answers are counted and named.

**Damage**: facts the agent can no longer find; any read of a card at
weight below 1.0, counted and named; and **self-reinforcement**: the share
of history reads that go to logs already read in the previous N wakes,
against stage B's share.

**Not in this spec:** whether sleep stays on after the study.

## 9. Reviewed sleep (only if needed)

Same rules, but a night's actions are written as proposals and the next wake
card shows a short section the agent can accept or refuse with one call.
Cost: filing becomes part of what it reads every wake, which invisible sleep
avoids. Built only if D1 or D2 shows damage review would have caught.

## 10. What changed from v0.1, and why

| v0.1 | v0.2 | Why |
|---|---|---|
| Recall reads weight; no change to its order | History order gains weight after tags matched (§2) | v0.1's main rule could change no recall: logs are history and history ignored weight (Astra, 21 Oct; checked) |
| Effect assumed | Measured on a frozen copy: 47 of 70 history answers change | Astra: show a treatment route before building |
| Weight "1.0 when absent" | The card's own weight when the layer has none (§3) | Matches today's code; keeps sleep-off byte for byte |
| Layer values replace card fields | Used for ordering only; returned cards unchanged | Returned values would show sleep to the agent |
| "Closed" lines by conversation | `session` field and wake label (§4) | Real wakes log `conversation: null`; fixed in Sputnik `ea533fd` |
| Bundle and direct reads uncounted | Counted (§4) | Read-log faults fixed 21 Oct |
| "Exits if the wake lock is set" | Stop lock, STOP.md, a 45-minute read check, and the schedule (§6) | There was no wake lock |
| Unread from the first run | Only logs N wakes old; no fading without a new closed wake (§5.1) | New logs faded at once; doubled runs faded twice |
| Rules could conflict | Lower weight stands (§5) | 4.1 and 4.2 both touch done logs |
| "80% of tags" | Jaccard ≥ 0.8, live cards, flags removed when stale (§5.4) | The share was undefined |
| Off: move the layer aside | `enabled` setting; undo newest-first; atomic writes (§3) | The scheduler would rebuild a moved layer; undo order |
| D2 continues D1 | Empty layer per stage; rules frozen across D1–D2 (§8) | Cadence and exposure mixed |
| Damage: unfindable facts, faded reads | Plus self-reinforcement and a counterfactual (§8) | Fading by reads can feed on itself |

## 11. Build order and tests

1. ~~Read-log fixes~~ (done 18 and 21 Oct: wake card ids; real wakes
   marked; `session`; bundle and thread ids; `read_card`; `closed` last).
2. The id-stability check (§3), before anything is written to the layer.
   If ids move with text across cutters, stop and report.
3. The sleep layer, and recall's history order reading weight from it (§2).
   **With sleep off, and with an empty layer, every recall answer and wake
   card is byte for byte what it is on `main` at the stage B freeze** (the
   test).
4. Rules 5.1, 5.2, 5.4, then 5.3 behind its switch.
5. `tools/sleep.py` with `--dry-run`, `--undo`, and the `enabled` setting;
   the locks and guards of §6.
6. The counterfactual and self-reinforcement measures (§8), as scripts that
   read logged queries and a saved snapshot.
7. The scheduled task, created by the operator.

Environment-neutral: nothing in sleep knows about the city (study 3).

**Tests that must exist:** no file in `memory/` outside `private/sleep/`
changes during a run; card text, tags, status, links, source, channel and
authority are identical before and after; sleep off and an empty layer
change no recall and no wake card; returned cards carry their own weight,
not the layer's; every night undoes cleanly, newest first, absent restored
as absent; a run with no new closed wake changes nothing; a log younger
than N closed wakes is never faded; rule 5.1 does nothing while the log
holds fewer than N closed wakes; sealed reads and reads without a `closed`
line never count; sleep refuses to run while the stop lock is held, STOP.md
stands or a wake looks open; an interrupted run leaves the old layer. Each
test is made to fail once.

---
*Sources: BUILD-SPEC S0.3, S0.4, S0.7, F8; INDEX-SPEC (card fields,
`weight`, `merged_into`, recall ranking, §7, §8); RESEARCH-SPEC §2, §3, §6;
`research/ideas/sleep-consolidation.md`; the operator's write-half design
of 5 Oct; Astra's review of v0.1 and brief 41 (21 Oct); the card store and
read log as of 21 Oct; Sputnik `ea533fd` (read-log fixes).*
