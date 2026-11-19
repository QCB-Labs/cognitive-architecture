# Idea: sleep consolidation

*Parked idea, not on the chain. Written by POE, for Audrie, 2026-09-29 (S48).
A possible branch off the cognitive architecture. It needs the associative
index (the base layer) before it can be built, and it must not hold up the
current link.*

**Status:** idea. Nothing here is a decision. The leads below are **unread**:
per CA §30.2, none of them is cited anywhere until someone has read the
source and checked the claim.

---

## Scope (Audrie, 2026-09-29)

This isn't only for Sputnik. It's a candidate **general pattern for
long-term persistent memory in LLM agents**, meant to work for any agent
that wakes, acts and has to remember across sessions. Sputnik is the first
test subject, not the point.

## Two halves of one memory system

Context exhaustion is live now: Sputnik's wake under AGY can't fit into a
Sonnet-sized context. Two things cause it, and each half fixes one.

- **The CA's half: bounded reads.** Each wake loads only what it needs, and
  no retrieval can exceed the context budget (CA invariant 8; §14.5 cost
  bounding, which the spec extends to every read tool). The associative index finds the right small slice. This
  protects the wake.
- **Sleep's half: bounded growth.** Even with perfect retrieval, the store
  keeps growing: duplicates, stale beliefs, near-identical lessons. Search
  gets noisier and the right slice gets harder to pick. Sleep keeps the
  store healthy by merging, summarising, flagging superseded beliefs and
  letting noise fade.

| | Result |
|---|---|
| CA without sleep | Small reads from an ever-growing junk drawer. Recall slowly decays. |
| Sleep without the CA | A tidy store, but whole-file reads still exhaust the context eventually. |
| Both | Each wake reads a small slice from a store that stays organised. |

**The caution:** bloat fails slowly and visibly. Consolidation fails
quietly: true things lost, beliefs distorted ("Useful Memories Become
Faulty", arXiv 2605.12978, verified 2026-09-29). It trades one failure for
another, and the research has to show the trade is worth it. So the raw
record stays untouched and the damage is measured, even if the sleep is
invisible to the agent.

## Where this sits in the CA spec

The spec is **not** silent on this. Sleep is its **§14 Consolidation**,
layer **L5**, and the wake cycle (§18) already ends in a step named SLEEP.
It already has: "consolidation creates new records, it never erases
history" (principle 9); output starts as a `candidate`; proposals,
acceptances and rejections are retained; §14.3 "consolidation is not
compression"; §A.8 on untested compression bias.

So this idea is a proposal for **how to build L5**, plus three questions the
spec doesn't answer:

1. **What runs it:** a small local model on the agent's own machine.
2. **Invisible vs reviewed:** the spec leans reviewed (candidates are
   validated). The invisible arm would change how L5 works.
3. **Forgetting:** the spec lists decay but says consolidation never erases.
   Forgetting-as-a-feature research could push on principle 9. The most
   sensitive of the three.

It also answers an open item: **§14.5 "Still unspecified: tiered
consolidation over already-derived objects"**, i.e. consolidating summaries
rather than raw episodes. That's where summary-of-summary drift lives.

**Possible rework (Audrie, 2026-09-29, not decided):** bind the associative
index (bounded reads) and L5 sleep (bounded growth) into the spec and the
research design as two strands of one memory system, rather than a base layer
and a late layer five steps apart.

## The idea

Sputnik's memory grows every wake, and every wake reads more of it. A person's
doesn't work that way: during sleep the brain replays the day, files what
matters and prunes the rest, and the person never knows it happened.

So: give the agent a **sleep**. Between wakes, a small open-source model runs
on the agent's own machine (this PC; a cloud VM was dropped on 2026-10-07)
and does the filing:

- **Tags and links** new memory entries (the associative index).
- **Shrinks** big things: a week of mission logs into one page.
- **Finds** near-duplicate lessons and entries that contradict each other.
- **Flags** beliefs that later evidence has superseded (CA §13.2).

The **waking mind** stays the big hosted model (Gemini or Claude). The
**sleeping mind** is small, local and owned outright, so no provider can
switch it off (CA §27.1, model independence).

## Split the work by what each tool is good at

| Job | Tool | Why |
|---|---|---|
| City IDs, names, place and wake numbers | Plain code | Exact. A model guesses; code doesn't. (Fixes the Astrolábio ID mix-up, S47.) |
| "This reminds me of" links | Small embedding model | Tiny, fast on CPU, made for similarity |
| Summaries, merges | 3B chat model | Adequate for plain summarising |
| "Is this lesson superseded?" | 7–8B chat model | Noticeably better judgement; overnight speed is fine |

## Rough fit on the free Oracle Arm VM (estimates, not measured)

*Kept as a record. The cloud deployment was dropped on 2026-10-07, so sleep
would run on the operator's PC (a consumer graphics card),
which is a better fit for a small local model than this VM was.*

2 cores, 12 GB, no GPU (Oracle's page, checked 2026-09-29: 1,500 OCPU-hours
and 9,000 GB-hours a month, "equivalent to 2 OCPUs and 12 GB").

- An 8B model (compressed) needs ~5–6 GB and reads ~10–25 words a second.
  A 10,000-word file takes 10–15 minutes to read. Overnight work only.
- An embedding model plus an 8B model plus the MCP server and website fit
  in 12 GB.
- A loaded model holds 40–50% of memory, above Oracle's 20% idle line for A1
  VMs. That's real use, not a burner. (Idle rule: CPU p95, network and memory
  all under 20% for 7 days.)

**First, test locally:** run an 8B model through Ollama on this PC against
one of Sputnik's real memory files. Time it and judge the output before
planning any cloud work around it.

## Guardrails

1. **The raw record is never touched.** Sleep writes derived records beside
   it (CA principle 9). Silent overwrites are what the research spec measures
   (R2).
2. **Invisible to the agent, visible to the researcher.** Everything sleep
   does is logged and reversible outside the agent's view. "Hidden from
   Sputnik" never means "hidden from Audrie".
3. **The system holds authority, not the model.** Who said what, and with
   what authority, lives in system fields, never in model-written prose.
   Consolidation launders authority otherwise (see findings).
4. **His memory is his.** S47's lesson: tell Sputnik things, don't edit his
   files. Sleep builds a derived layer; it doesn't rewrite what he wrote.
5. **Small models are confident and wrong.** Mechanical jobs go to code and
   small models; creative outputs are marked as hypotheses only.

## The research question it opens

Biology says sleep is **invisible**: nobody reviews what their brain filed.
Invisible sleep is Audrie's original insight, not the risky option to be
designed out.

- **Arm A: invisible sleep.** Consolidation applies itself.
- **Arm B: reviewed sleep.** Every change is proposed; the agent decides.
- **Arm C: review only the identity core.** Values, relationships and
  commitments are reviewed; everything routine is silent.
- **Controls:** raw retrieval only, and a hand-curated set where affordable.
- **Measure:** coherence, read size, cost (the benefit); facts lost or
  distorted, authority changed, false supersessions (the damage), over many
  cycles.

Nobody has run this comparison (both research passes, 2026-09-29).

## What the research found (2026-09-29)

**This section is a map, not evidence** (see `research/METHODS.md`). It
summarises two AI-assisted literature searches (GPT-5.6 Sol, medium, via
Codex). Their raw outputs and prompts are kept privately, outside the repo.
Each source is linked. Every claim or number marked **[unreviewed]** came
from the search, not from reading the paper; the tag comes off only when the
claim has been checked against the paper itself (METHODS §4). arXiv IDs are
checked; journal DOIs are not yet.

**The case for invisible** (the search's argument, not yet ours to cite).
Reviewing every change turns storage maintenance
into more memory: the agent's filing becomes part of what it remembers and
competes with the world for context. Offline automatic consolidation protects
the waking context. *Not found:* evidence that unawareness itself helps.
Offline processing and a quiet mind are supported; unawareness as the cause
is not.

**The risk, measured.** ["Useful Memories Become Faulty When Continuously
Updated by LLMs"](https://arxiv.org/abs/2605.12978) (preprint, 2026):
continuously rewritten memory helps, then degrades, sometimes below no memory
at all. **[unreviewed]**

**Authority laundering (most important for Sputnik).** ["When Memory Becomes
Authority"](https://arxiv.org/abs/2608.01679) (preprint, 2026): consolidation
turned low-authority content into apparent authority in 48 of 49 set-ups
**[unreviewed]**. For Sputnik: a resident's email
slowly becoming "something Audrie told me". The CA already names this attack
(§8.4 "Durable attribution"). Their fix: system-held authority
labels checked at action time, unauthorised actions 16.9% to 0%
**[unreviewed]**.

**Synaptic tagging translates well.** [Frey & Morris 1997](https://doi.org/10.1038/385533a0);
[Redondo & Morris 2011](https://doi.org/10.1038/nrn2963). An experience is
tagged when it happens; later signals decide whether it lasts.
**[unreviewed]** For an agent: a tag means **eligible to keep, not true**. Signals
are objective (novelty, outcome, independent repetition, goal relevance),
never self-rated importance.

**Forgetting as reduced findability, not deletion.** [Richards & Frankland
2017](https://doi.org/10.1016/j.neuron.2017.04.037) **[unreviewed]**. Keep everything; take stale material off the default search surface.
This fits principle 9, which then needs no change.

**Reads must not rewrite.** Reconsolidation ([Nader et al.
2000](https://doi.org/10.1038/35021052)): recall makes a memory changeable
**[unreviewed]**. An agent that rereads everything every wake keeps
re-exposing all of it to drift. Retrieval should be sparse and cue-driven,
and only retrieval plus new evidence makes a memory eligible for update.

**Three passes, not one.**
1. Careful (NREM-like): link, dedupe, extract only what sources directly
   support, flag contradictions without picking a winner.
2. Creative (REM-like): patterns, lessons, analogies, stored as hypotheses
   only.
3. Pruning (homeostatic): lower findability of stale and redundant material;
   the identity core stays above a floor.

**Prior art to read.** [SCM](https://arxiv.org/abs/2604.20943) already does
tagging, two sleep phases and forgetting, on tiny tests.
[REALM](https://arxiv.org/abs/2609.16053): reconsolidate only the retrieved
part. [Agent Zero Memory](https://arxiv.org/abs/2608.29606):
provenance-locked memory. All preprints, 2026. **[unreviewed]**

## Requirements for the associative index brief

So sleep can plug in later without rebuilding the index:

1. **Never overwrite the raw record.** Append only.
2. **Tag at write time** with eligibility signals, not importance.
3. **The system stores source and authority** as fields, never in the
   model's prose.
4. **Every entry has a slot for "merged into / superseded by"** and for
   findability, so forgetting lowers access instead of deleting.
5. **Reads never write.** Retrieval events are logged separately.

## If it becomes a branch

- Depends on: the associative index (base layer), built to the requirements
  above.
- Belongs in: `mind/` (the sleeper) and `research/` (the arms).
- Answers: CA §14.5's open item, tiered consolidation over derived objects.
- Decide then: which model, where it runs (VM or this PC), whether the arms
  join the main study, and whether index and sleep are rewritten as one
  paired memory system in the spec.

---

*Drafted by Claude Opus 5.5 (POE desk, Claude Code) from conversation with
Audrie, 2026-09-29. Ideas and direction: Audrie. Reviewed by Audrie: pending.*
