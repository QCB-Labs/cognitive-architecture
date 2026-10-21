# Links v0: build spec

*v0.1 DRAFT, 21 Oct 2026. Not decided: for Audrie to read. Written by POE,
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
how recently he used them. Opening one is a read, and a read brings it back
up.

- **Bounded:** labels cost a few hundred bytes, not the cards.
- **Continuity:** nothing linked becomes unreachable. A card he hasn't used
  in a long time sits lower in the list; it doesn't leave it.
- **Like memory, as far as it goes:** recalling one thing brings its
  associations to mind; what is used stays near, what isn't fades back, and
  using it again brings it forward. A guide for the design, not a claim
  about minds.

## 2. Where links come from (v0: derived, not written)

v0 derives links from tags the cutter already writes. The agent does
nothing new, and his protocol does not change.

- **Entity tags** are the link points: `resident:`, `place:`, `thing:`,
  `note:`. (On 21 Oct: 103 residents, 329 places, 257 things, 685 notes.)
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
3. **Rank** by: the strength of the connection, then weight (sleep's, once
   it exists; until then every card's own, so no effect), then newest
   first. **Strength** counts each shared tag by how rare it is, so a hub
   tag on hundreds of cards (his home place: 333) counts for little and a
   tag on two cards counts for a lot: the sum over shared tags of
   `1 / log2(1 + cards carrying the tag)`.
4. List the first **12** (a setting, `recall_linked_listed`) as labels:
   id, label, kind, bytes, and the tag that links it.
5. The list is the **first to give way** when the whole answer is over its
   limit, before `same_file`, `people` and `left_out_cards`. Card text is
   never dropped for it (INDEX-SPEC §7, unchanged).

**Measured on 21 Oct, Halfverse:** a recall of `resident:260` matches 37
cards; one hop through their entity tags reaches 902 more. That is why the
list is ranked and capped, and why hub tags count for little.

## 4. Reads

- Opening a linked card with `read_card` is a read, logged as it is today.
- The read log also records which ids were **offered** in the linked list,
  apart from the ids **returned** in full. Offered is not read: sleep counts
  only returned and opened cards as reads. The study needs both, to see
  whether he follows the chain.

## 5. With sleep (later)

Sleep ranks the chain. A faded card moves down the linked list, never off
it while its tag is shared. This is what makes fading safe: the way back is
always shown. SLEEP-SPEC's self-reinforcement measure (§8 there) is read
against this list.

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
2. Recall adds `linked` to its answer; the read log adds `offered`.
3. Settings in `config/cards.json`: `recall_linked_listed` (12),
   `link_tag_prefixes`. `0` turns the list off.

**Tests:** with the list off, every recall answer is byte for byte what it
is on `main` at the stage B freeze; the full cards returned and their order
never change with the list on; the list never holds a returned or
left-out card; a hub tag ranks below a rare one; the list gives way first
under the answer limit, and card text never does; offered ids are logged
and never counted as reads; nothing in `memory/` changes. Each test is made
to fail once.

## 7a. Decided in conversation, 21 Oct evening (Audrie)

- **Grouped by kind.** The list comes in groups (threads, places, things,
  notes, wakes), each with a small cap; `note:` links at most 3, so precise
  but rare note tags can't crowd out people and places. In stage C the
  groups come in a fixed order and items by link strength; with sleep
  (stage D) group order and item order both follow accessibility, so if #66
  lives in notes more than places, notes rise.
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
  stage B gives; he loses only the labels. Kept, so stage C's effect can be
  told from time passing.
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

- Two hops (person to place to thing) or one? v0 is one hop from what was
  returned; the second hop is one more recall, by choice.
- Should `note:` tags (685, mostly one card each) be link points, or only
  names, places and things?
- When does the agent write explicit links, with a reason? Not in v0.

---
*Sources: the operator's write-half design (5 Oct), "The four things that
matter"; INDEX-SPEC §2.3 (link types), §7 (recall), §8 (open questions);
SLEEP-SPEC v0.2; the card store and read log as of 21 Oct.*
