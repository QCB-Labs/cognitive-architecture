# Links v0: build spec

*v0.2, 10 Nov 2026: Audrie's decisions of 30 Oct and 10 Nov added (§§2, 3a, 4, 9).
v0.1 DRAFT, 21 Oct 2026. Not decided: for Audrie to read. Written by POE,
for Audrie, from her design (5 Oct, "the four things that matter": linking
first) and her account of 21 Oct, using Halfverse as the example. Review
welcome.*

## 0. What this is

Linking was first in the write-half design: "a card that mentions Halfverse
points at the Resident #260 card, and that card points back at the wakes."
It was never built. On 21 Oct every one of his 1,762 live cards has an
empty `links` field, and nothing writes one. Tags stand in: recall finds
cards by tag, and its answer names a few neighbours (`people`, `same_file`).
Going further, person to place to thing to note, takes a new recall at
every step, with a tag he has to notice himself.

Links v0 makes the chain part of every recall answer, cheaply.

## 1. The idea, in Audrie's example

He recalls Halfverse. The answer gives, in full, what it gives today: the
resident card and current impression first, then the rest that fits the
budget. **Below that comes a linked list:** the threads, places, things,
notes and wakes connected to what was returned, as labels only (id, label,
kind, size), ordered by how strongly they connect and, once sleep runs, by
their sleep weights (§3). Opening one is a read; sleep applies its
restoration rules at the next run.

- **Bounded:** labels cost a few hundred bytes, not the cards.
- **Continuity:** a shared tag keeps a card eligible, but caps and answer
  limits can hide its label. Such omissions are counted, not prevented
  (SLEEP-SPEC §2, finding 4; Audrie, 23 Oct).
- **Like memory, as far as it goes:** recalling one thing brings its
  associations to mind; what is used stays near, what isn't fades back, and
  using it again brings it forward. A guide for the design, not a claim
  about minds.

## 2. Where links come from (v0: derived, not written)

v0 derives links from tags the cutter already writes. The agent does
nothing new, and his protocol does not change.

- **Entity tags** are the link points: `resident:`, `place:`, `thing:`.
  (On 21 Oct: 103 residents, 329 places, 257 things.) **`note:` is not a
  link point in v0** (Audrie, 10 Nov): its 685 tags are mostly on one card
  each, so they would add noise, not connections. Adding `note:` back to
  `link_tag_prefixes` turns it on, with the cap in §7a.
- Two live cards are **linked** when they share an entity tag.
- `name:`, `kind:`, `date:`, `wake:` and `ref:` are not link points: they
  describe a card rather than connect it.

Explicit links (`{rel, to}` in the `links` field, written by the agent or
the cutter, with a reason) are left for later. Whether a shared tag is
enough, or some links need a stated reason, has been an open question in
INDEX-SPEC since 5 Oct; v0 answers "a shared tag is enough" and measures
it.

## 3. The linked list in a recall answer

After recall chooses the cards it returns (unchanged from today):

1. Take the entity tags of the returned cards, leaving out the tags asked
   for (those are already the match).
2. Candidates: live cards carrying any of those tags, not already returned
   or listed in `left_out_cards`.
3. **Rank within kind.** In C: strength descending, the card's own weight
   descending, newest first, then card id ascending. In D: effective weight
   descending, strength descending, newest first, then card id ascending.
   Effective weight is the layer's weight when sleep is enabled and an
   entry exists, otherwise the card's own. Newest means card date descending.
   With sleep off or an empty layer, use C's order, including group order.
   **Strength** is the sum over shared entity tags from step 1 of
   `1 / log2(1 + cards carrying the tag)` in the live store.
   A hub tag on hundreds of cards counts for little; a rare tag for more.
4. Group by kind under §7a, apply each kind's cap, concatenate in group
   order, then keep the first **12** (`recall_linked_listed`) as labels:
   id, label, kind, bytes, and the tag that links it.
5. The list is the **first to give way** when the whole answer is over its
   limit, before `same_file`, `people` and `left_out_cards`. Card text is
   never dropped for it (INDEX-SPEC §7, unchanged).

**Measured on 21 Oct, Halfverse:** a recall of `resident:260` matches 37
cards; one hop through their entity tags reaches 902 more. That is why the
list is ranked and capped, and why hub tags count for little.

## 3a. Also on `read_resident` and `read_thread` (Audrie, 30 Oct)

In stage B he called `recall` 3 times in 10 wakes, but read residents and
threads every wake. So the list also goes where he already reads:

- `read_resident(handle)` and `read_thread(title)` return their file text
  as today, unchanged, then the linked list below it.
- Their **returned cards** (§3 step 1) are the live cards cut from that
  file. The tags asked for are that file's own: the resident's
  `resident:` tag, or the thread's own entity tags in its heading.
- Ranking, caps, the 12-label limit and the read log follow §§3, 4 and
  7a exactly as for recall.
- `read_resident()` with no handle (the index) and `read_threads` (the
  list) get no linked list.
- If the file has no cards yet (written this wake, not yet cut), the
  list is empty and says so in one line.

## 4. Reads

- Opening a linked card with `read_card` is a read, logged as it is today.
- The read log also records which ids were **offered** in the linked list,
  apart from the ids **returned** in full. Offered is not read: sleep counts
  only returned and opened cards as reads. The study needs both, to see
  whether he follows the chain.
- **A read belongs to the wake whose conversation made it** (Audrie, 10
  Nov). The log's `wake` field is the meter's count at the time; after a
  wake's close marker the same conversation sometimes reads on, and those
  rows carry the next wake's number (28 of 742 reads, W282-W324). Stage C
  counts per wake by `conversation`, with `wake` taken from that
  conversation's first row. The agent is not stopped from reading after
  close.

## 5. With sleep (later)

Sleep ranks the chain under §§3, 7a. A faded card remains a candidate
while its tag is shared, but may fall beyond a kind cap, the total cap or
the answer limit. A shown route back is not guaranteed; omissions are counted
(SLEEP-SPEC §2, finding 4; decided by Audrie 23 Oct). Its self-reinforcement measure (§8 there) uses C as the reference.

## 6. What links never do

- Change what recall returns in full, its order, or its budgets.
- Change the wake card. (A linked list on the wake card is a later
  question.)
- Write to his files or cards, or change the `links` field. v0 derives;
  it stores nothing.
- Know about the city beyond the four tag prefixes, which live in config
  (`link_tag_prefixes`), so another world names its own (study 3).

## 7. Build order and tests

1. The ranking as a pure function: (returned cards, store, weights,
   settings) to a list of labels.
2. Recall adds `linked` to its answer; so do `read_resident(handle)` and
   `read_thread(title)` (§3a); the read log adds `offered`.
3. Settings in `config/cards.json`: `recall_linked_listed` (12),
   `link_tag_prefixes`. `0` turns the list off.

**Tests:** with the list off, every recall, `read_resident` and
`read_thread` answer is byte for byte what it
is on `main` at the stage B freeze, with sleep off; with links on, sleep
off and an enabled empty layer each preserve stage C byte for byte; the
full cards returned and their order never change merely by enabling links;
the list never holds a returned or left-out card; at equal weight, a hub
tag ranks below a rare one; the list gives way first
under the answer limit, and card text never does; offered ids are logged
and never counted as reads; group scores, ties and item order follow §§3,
7a, including caps and trimming; nothing in `memory/` changes. Each test
is made to fail once.

## 7a. Decided in conversation, 21 Oct evening (Audrie)

- **Grouped by kind.** The list comes in groups (threads, places, things,
  notes, wakes), each with a small cap; `note:` links at most 3 (off in
  v0, §2), so precise
  but rare note tags can't crowd out people and places. In stage C the
  groups come in a fixed order; both group and item order follow
  accessibility in D. **Proposed clarification, 23 Oct, finding 3:** use
  the fixed order just listed in C, with items following §3. Any
  other kinds follow in kind-name order. In D, a nonempty group's score is
  the mean effective weight of all its candidates before caps. Groups sort
  by score descending, with C's group order breaking ties; empty groups
  are omitted. Items follow D's order in §3. Caps and trimming follow only
  after ranking. This defines accessibility from the per-card weights;
  no separate group state is added. Recovery: omissions counted, not guaranteed (§5).
- **One hop only, in v0.** More hops over shared tags mostly add noise
  (Halfverse: 902 cards at one hop). Deep chains follow typed links instead,
  weaker at each hop, as `associate` in the mind server (BUILD-SPEC §5,
  T11; CA §16). So there is no `hops` setting in v0 and no protocol line to
  decide.
  **Multi-hop belongs to traceability.** "Why do I believe this?" is a
  walk of several steps by nature: a belief back to the episodes and
  observations behind it (CA §6). That walk follows typed links
  (`derived_from`, `from`, `cites`), not shared tags, so it is precise and
  doesn't fan out the way tag hops do (Halfverse: 902 cards at one hop). So
  deep chains are stage E's; association stays shallow.
- **A links withdrawal is safe.** With the list off, recall is exactly what
  stage B gives when sleep is also off; he loses only the labels. Kept, so
  stage C's effect can be told from time passing.
- **No rumination (CA §11.1).** "Retrieval does not reinforce": being
  recalled never raises salience. The list's order follows use
  (accessibility, CA §11) but must not amplify it: a read restores a card's
  weight to where it stood, never above it, and nothing here writes
  salience.

## 7b. Where this sits

CA §32.1 (index and dossier) applied to recall: the list is the index tier,
the full cards the dossier. The untyped forerunner of INDEX-SPEC §2.3's
`about`. The first build of what CA §16 scores as relationship and location
relevance. Separate from the CA §6 evidence chain (`derived_from`,
`used_in`), which is about what is true, not what is reachable. Typed
explicit links (`from`, `cites`) would feed traceability and belong with
stage E.

## 8. A limit, stated (Audrie, 21 Oct)

**His memory is only what he chose to write.** His cards are cut from his
logs, resident files, threads and lessons. The wake itself (every tool
call, what residents said, what he read) stays in the driver's own
conversation record and never reaches his memory. So anything he did not
write down is gone for him, and the links, derived from his writing, only
join what he already judged worth keeping. They can't surface what he
overlooked.

The study reports continuity in that sense: continuity of what he recorded,
not of what happened. For comparison, Riverbed keeps whole transcripts and
draws its memories from them, so it can recover what a companion never
noted, at a cost in storage and extraction that this design avoids.

The transcripts do exist, in the driver's records on the operator's
machine. Whether they become a source (and whose decision that is, given
they hold residents' words) is not part of v0.

## 9. Open

- When does the agent write explicit links, with a reason? Not in v0.

Settled, 10 Nov (Audrie): **one hop** (as §7a); **`note:` is not a link
point in v0** (§2). On 30 Oct: the list also goes on `read_resident` and
`read_thread` (§3a).

---
*Sources: the operator's write-half design (5 Oct), "The four things that
matter"; INDEX-SPEC §2.3 (link types), §7 (recall), §8 (open questions);
SLEEP-SPEC v0.2; the card store and read log as of 21 Oct.*
