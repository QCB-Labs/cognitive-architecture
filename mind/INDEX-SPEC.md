# Memory cards and the associative index: build spec v0.3

*Stage 0 of `BUILD-SPEC.md`, in detail. Draft for review.*

*Decision (Audrie, 2026-09-30): **Option B**: memory becomes cards, and the
cards are the truth. The old memory files become generated views.*

***Changed on 2026-10-05 (Audrie): the files stay the original.** The agent
keeps writing files. The tools cut every file at its headings into small
labelled cards and link them. The cards are a cut of the files and can be
rebuilt from them at any time; nothing is generated back into a file. This
replaces the second half of Option B. The read half below stands as built.
The write half (§8 to §10) is redrawn in §8.*

**What is built, as of 2026-10-08** (in Sputnik's repo; the template is
behind, see §10):

| Part | State |
|---|---|
| Card store, tags, migration, round trip, re-cut on write (R1 to R5) | built |
| `recall`, `read_card`, the read log (R6) | built; the whole answer is limited since 2026-10-07 (§7) |
| `read_wake_card` (R7) and the protocol's read steps (R8) | built; shows one wake back since 2026-10-07 (§6) |
| Logs and resident files cut small, keyed and labelled (§5.1a) | built 2026-10-07 |
| Goals and projects as small files | brief written, not built |
| Threads as small files, with a way to close one | not written |
| Lessons as small files; a file per remembered thing | not started |
| Sleep | not started |

---

## 0. Read this first

This is a portable brief. You can build from it without the conversation
that produced it.

**Read before starting:**
- `mind/BUILD-SPEC.md`: §0 (builder rules) and **Stage 0** (why this exists,
  the measured numbers, the five requirements).
- `spec/COGNITIVE-ARCHITECTURE.md` §1.1 (three continuities), §8.4 (origin
  survives storage), §9.4 (commitments are not threads).
- The template repo `agent-harness-template`: `tools/harness_mcp.py`,
  `naming.json`, `GEMINI.md`.

**Builder rules (from BUILD-SPEC §0, repeated because they matter):**
1. **Don't commit.** Leave changes in the working tree. Audrie commits.
2. **Your own words and code.** Reuse our template freely. Copy nothing from
   Waypost, Cairn or PR #1.
3. **Make every check fail once** before trusting it.
4. **No real memory in the template repo.** Sputnik's files are private. Test
   against a copy kept in a gitignored folder (`fixtures/private/`), never
   committed. Committed tests use small made-up fixtures.
5. **Stop and report** when something here can't be built as written.
6. **Don't edit the agent's wording.** Migration cuts text into cards. It
   never rewrites, summarises or "cleans" the agent's words.

**Where to build:** the template (`agent-harness-template`) first. Sputnik
gets it in a later ticket (R8). Use the template's logical names from
`naming.json` (`lessons`, `open_threads`, `continuity`, `goals`, `journal`,
`residents`), never a scheme's display names.

**Build in two halves.** The **read half** (R1–R8) fixes the context problem
and changes nothing about how the agent writes. The **write half** changes
how the agent writes. Build and review the read half first. Since
2026-10-05 the write half is the plan in §8, not tickets W1–W6.

**Sputnik first, since 2026-10-04.** The read half was built in the template
and ported. Everything after it has been built in Sputnik's repo against his
real files and is carried to the template in catch-up passes.

---

## 1. What changes, in one paragraph

Today the agent's memory is a few big files, and every wake reads them whole
(~58,000 tokens for memory alone, growing every wake). After this build, each
memory is a **card**: one lesson, one thread, one goal, one section of a log,
one dated observation of a resident. Cards have a kind, a label, tags, a
status and links. A wake starts by reading one **wake card** built from the
store, always the same seven sections, always inside a byte budget.
Everything else is **recalled** by tag when needed. The files the agent
writes stay the original (2026-10-05); the cards are cut from them after
every write.

---

## 2. The card

### 2.1 Fields

| Field | Set by | Meaning |
|---|---|---|
| `id` | system | Stable, never reused. Form: `<kind>-<number>`, e.g. `lesson-0107` |
| `kind` | system (migration) or agent (new card) | One of the kinds in §2.2 |
| `text` | agent | The card's content, in the agent's words. Markdown allowed |
| `title` | agent, or system for a piece of a log or a resident file | Short label. For threads: the bold heading line. For a piece of a log or a resident file: a label built by code from facts it already has (§5.1a) |
| `role` | system | `current` or `history` (§5.1a). A card without one is treated as `current` |
| `tags` | system | Extracted by code from `text` and `title` (§4). Never written by the model |
| `status` | system, on agent request | `live`, `done`, `superseded`, `merged`, `recheck`, `structure` |
| `links` | agent or system | List of `{rel, to}`. `rel` in §2.3 |
| `created_at` | system | UTC time the card was first written |
| `updated_at` | system | UTC time of the last change |
| `wake` | system | Wake number the card was written or last changed in |
| `source` | system | Where the content came from: `self`, `operator`, `peer:<name>`, `world:<id>` |
| `channel` | system | How it arrived: `session`, `email`, `world`, `migration` |
| `weight` | system | Findability, 0.0–1.0. Starts at 1.0. Sleep lowers it. Never deletes |
| `origin` | system | File and position the card was cut from. For a piece of a log or a resident file it also holds `key`, the piece's name within its file (§5.1a) |

`structure` marks a piece that holds only a file's shape, such as a heading
or a preface. It is kept so the file can be rebuilt byte for byte. It is
left out of the wake card and of recall. Built in Sputnik `773ff06`.

**Rule:** the model never sets `id`, `tags`, `role`, `created_at`,
`updated_at`, `wake`, `source`, `channel`, `weight` or `origin`. If a write tries to, refuse
it with a reason.

### 2.2 Kinds

| Kind | Means | Comes from today (logical name) |
|---|---|---|
| `goal` | What the agent is working towards | `goals` |
| `commitment` | A promise made to someone. Owed | nowhere clean yet (scattered) |
| `thread` | Something the agent **may** return to. **Not owed** | `open_threads` |
| `rule` | Short, practical, keep in mind | `lessons` (short entries), `city_rules` |
| `reflection` | The agent's thinking about what it saw | `lessons` (long entries) |
| `decision` | A settled choice and its reason | `continuity` (retired 2026-10-03; the kind stays valid so old cards load) |
| `relationship` | What the agent knows about someone. One card per piece of a resident file since 2026-10-07 | `residents` |
| `log` | One wake's record. One card per section since 2026-10-07 | `journal` (mission logs) |
| `handover` | What the next wake needs. One per wake | not built: the newest log's own sections do this job (§6, §8) |

`soul`/identity and governance are **not** cards. They stay as they are and
are always read whole (§6).

### 2.3 Link types

| `rel` | From → to | Means |
|---|---|---|
| `serves` | thread or commitment → goal | This work is for that goal |
| `from` | commitment → thread | This promise came out of that conversation |
| `supersedes` | any → same kind | This replaces that. The old card gets `status: superseded` |
| `merged_into` | any → same kind | Two cards were the same. Set by sleep, later |
| `about` | any → relationship | This card concerns that person |
| `cites` | reflection → any | This thinking draws on that |

---

## 3. Storage

- **One append-only file:** `{memory}/cards/cards.jsonl`. Every write appends
  a full new version of the card as one JSON line. Nothing is ever edited or
  removed in place.
- **The current state** of a card is its **last** line. A card's history is
  all its lines.
- **A derived lookup** (`{memory}/cards/index.json`: id → last line, tag →
  ids) can always be rebuilt from `cards.jsonl`. If it's missing or broken,
  rebuild it; never trust it over the JSONL.
- **Source files may sit outside `{memory}`.** `goals` (and identity,
  governance) live at the agent's repo root in both Sputnik and the template.
  Migration reads each logical file from where `naming.json` puts it,
  relative to the **repo root**, not the memory folder. (v0.2: brief 01's
  private fixture copied only `memory/`, so goals weren't migrated.)
- **The files are the original** (2026-10-05). The agent writes files; the
  store is cut from them and is never written back. Rebuilding a file from
  its current cards is kept as a test (§5.3), not as a way of producing
  files. (v0.2 planned the reverse: files regenerated from cards after every
  write, under a "Generated from cards. Do not edit." header. Not built.)
- **Archive:** previous versions of generated views go to
  `{memory}/archive/`, not beside the live file. No `.bak` files in
  `{memory}`.

---

## 4. Tags

Tags make a card findable. They are extracted **by code** from `title` and
`text`. They never mean "important" or "true".

### 4.1 Patterns

Patterns live in a config file, `{memory}/cards/tag-patterns.json`, **not in
code**. The template ships a generic set. The city's patterns are an
**environment pack** (CA study 3 moves the mind to other worlds; code must
not know about the city).

Generic set (template):

| Tag form | Pattern (examples) |
|---|---|
| `wake:W134` | `W` followed by 3+ digits |
| `date:2026-09-30` | ISO dates |
| `kind:<kind>` | added from the card's kind |

City environment pack (Sputnik):

| Tag form | Matches in text |
|---|---|
| `resident:188` | the word resident with `#188`; or a handle from `residents/index` with **that handle's own index ID** right beside it, as in `Glimmerbell (#382)` |
| `place:1207` | `Place 1207`, `Places 1204 & 1205`, `[195]` in a routing context |
| `continent:1201` | `Continent #1201` |
| `note:25540` | `Note #25540` |
| `thing:4741` | `Thing #4741` |
| `post:7164` | `Post #7164`; `Dispatch #5447`, `Dispatches #5991, #5996 & #6144` (a Square post) |
| `kind-id:39` | `Kind #39` |
| `name:glimmerbell` | a resident handle listed in `residents/index` |

### 4.2 Rules

- A pattern that matches ambiguously (`#188` with no context) gets the
  generic tag `ref:188`. Don't guess the type.
- Tags are lower case.
- **`resident:<n>` only ever holds a city resident ID** (the number the
  city uses as `maker_id` / `owner_id`; checked 30 Sept: tel's things show
  361, tel's recorded ID). Other services number the same agent differently
  (Sputnik is city #66 and Square citizen 688). Those get their own tags,
  `square:<n>` and `market:<n>`, and never `resident:`. (v0.2)
- **The resident index is the authority for who has which ID** (added
  1 Oct, after review of brief 04). The pack reads handle and ID from each
  line of `residents/index` (table rows or bullets). A handle found in the
  text gets `name:<handle>`. It gets `resident:<id>` as well only when the
  index's ID for that handle stands right beside the name. A different
  number beside the name stays `ref:<n>`: that is a disagreement between
  his records, and the tag must not hide it. A name that isn't in the index
  stays `ref:<n>` too.
  Why: his threads write people as `Name (#id)`. Before this rule not one
  thread carried a `resident:` tag, and no card carried a `name:` tag (the
  pattern expected bullets; his index is a table), so recall by the people
  present found nothing. After it, 43 of his 47 live threads carry one.
- Handles are matched without accents, so `Astrolábio` in the text finds
  the index handle `astrolabio`.
- **Square people get no person tag.** They are not city residents and no
  index of them exists in his memory, so there is nothing to check a name
  against. His Square threads are found by their `post:` tags. If he ever
  keeps a Square index, it becomes a second name source in the pack; that
  is his to decide.
- `name:` tags are loose on purpose: a handle that is also a common word
  ("five", "founder") matches wherever the word appears. `resident:` tags
  are the precise ones. Recall for a person uses `resident:<id>`.
- Re-running extraction on the same text gives the same tags.
- Build a **tag test set** from real text (R2): at least 30 lines from the
  private fixture, each with the tags it should get. Check the extractor
  against it. Make it fail once on purpose.

---

## 5. Migration (today's files → cards)

### 5.1 How each file is cut

| Logical file | Cut on | Kind | Notes |
|---|---|---|---|
| `lessons` | each `## <date-stamp>` heading | `rule` or `reflection` (§5.2) | The heading's stamp is `created_at`. One heading = one card, even if it holds several bullets |
| `city_rules` | each top-level bullet or `##` heading | `rule` | Status follows the file's own section (§5.2a). `created_at` is the entry's own first date, where it wrote one |
| `open_threads` | each top-level `- **...**` item | `thread` | The bold line is `title`. Items under `## Resolved threads` get `status: done` |
| `goals` | each goal heading or top-level item | `goal` | Keep the file's order |
| `continuity` | each top-level bullet (`- `) inside its `##`/`###` sections | `decision` | A section heading, and any text before its first bullet, belong to the first bullet's card. Text before the first heading belongs to the first card. (v0.2: v0.1 cut on headings and made three giant cards from Sputnik's file) |
| `journal` | each level-2 heading (`## `); the text before the first one is the header | `log` | `wake` from the file name. See §5.1a. (v0.2: one card per file) |
| `residents` | the header; each dated bullet under the observations heading; each other `## ` section | `relationship` | `tags` include `resident:<id>`. See §5.1a. (v0.2: one card per dossier file) |

The `continuity` file was retired on 2026-10-03; its row is kept for stores
that still hold `decision` cards.

### 5.1a Logs and resident files: small pieces, keys, roles, labels (built 2026-10-07)

A mission log as one card ran to 7 to 14 KB, and a resident file was one
card. A recall about one person returned whole logs and crowded out
everything else, and every log showed in a list under the same title.

**The cut.**
- A log is cut at every `## ` heading. A `### ` heading stays inside its
  section. A rule line and blank lines stay with the piece above them. A log
  with no `## ` heading stays one piece.
- A resident file is cut into the header (down to and including the
  observations heading line), one piece for each dated bullet under that
  heading, and one piece for each other `## ` section. A bullet that doesn't
  start with a date belongs to the piece above it.
- Which heading holds the dated entries is a setting, matched as a pattern.
  A file that doesn't fit is cut at its `## ` headings only. Nothing here is
  an error.

**A key** (`origin.key`) names a piece within its file and does not depend
on where the piece sits: `header`; a section's heading text, lower-cased,
with runs of anything that is not a letter or digit turned into one hyphen;
`entry:<date>` for a dated bullet. A second piece with the same key gets
`-2`, a third `-3`, in file order.

**Matching is by key, not position**, for these two kinds of file. Same key:
same card id, and a new version only if the text, label, status, role or
origin changed. A key the file no longer has: the card gets status `done`
with the reason `removed from source file`. A key the store hasn't seen: a
new card. Why: adding an observation just above the impression, and
changing the impression, in one write, made the position matcher hand the
impression's id to the new observation. (Echo's finding 8 of 2 Oct, seen
live on 4 Oct when a thread added at the top of a file took the id of the
thread below it. Threads, goals, lessons and rules are still matched the
old way until each becomes one small file.)

**A role.** Every piece of a log is `history`. In a resident file each dated
bullet is `history`; the header and every other section are `current`.

**A label** (the card's `title`), built only from facts the cutter already
has. Nothing is summarised or reworded. Patterns are settings:

| Piece | Label |
|---|---|
| log header | `W137 · header` |
| log section | `W137 · What I Plan Next` (the heading's own text) |
| a log named by date | the date in place of the wake number |
| resident header | `Resident #260 · <handle> · header` |
| resident section | `Resident #260 · <handle> · <heading>` |
| resident dated bullet | `Resident #260 · <handle> · 2026-10-05` |

**Tags that belong to the file.** Every piece of a log carries that log's
`wake:` tag and its `date:` tag. Every piece of a resident file carries
`resident:<id>` and `name:<handle>`. Only those: a place or person named in
one section is not tagged onto the others.

**A store cut the old way** is re-cut once. Each old one-card-per-file card
gets status `done` with the reason `re-cut into keyed pieces`; its text and
history stay readable by id. A second run changes nothing. On Sputnik's
memory (2026-10-07): 136 logs became 661 cards and 72 resident files became
272; every file rebuilt byte for byte; the store went from 2.29 MB to
4.86 MB.

**The log's own shape.** Since 2026-10-06 Sputnik's protocol gives his log
four named sections, each with a definition: `Waiting, Due, Deferred and
Resolved` (four short lists), `What Happened, and Why`, `Observations`,
`What I Plan Next`. The cut needs no knowledge of these; the wake card finds
two of them by pattern (§6). Of his first 97 logs there were 36 layouts.
Where the protocol named a section he followed it within one wake.

**Resident with no ID.** If a dossier's ID is missing (`Resident ID: —`),
don't stop and don't guess. The card gets `name:<handle>` instead of
`resident:<id>`, plus status `recheck`, and the migration report lists it.
Filling the ID is the agent's job on a wake, not migration's. (Added
2026-09-30 after brief 01 found four such dossiers.)

If a file doesn't fit its rule (no headings, mixed formats), **stop and
report** with examples. Don't invent a rule.

### 5.2 Rule or reflection

Code proposes, a human or the agent confirms:
- Proposed `rule`: under 400 characters and no `###` subheadings.
- Proposed `reflection`: anything else.
- Every proposal is written to `{memory}/cards/kind-review.md` for
  confirmation. Until confirmed, the card carries status `recheck`.

### 5.2a A rulebook's sections set status (added 1 Oct)

His rulebook already sorts its entries: Confirmed, Proposed, Retracted. The
environment pack says which heading means which status
(`section_status` in the pack, not in code):

| Section heading starts with | Card status | In the wake card |
|---|---|---|
| anything else (Confirmed, the introduction) | `live` | shown under Rules |
| `Proposed` | `recheck` | not under Rules; queued in "What needs checking" |
| `Retracted` | `done` | not shown; still readable by id |

- Headings themselves stay `live`, so the Rules section still shows the
  shape of the file. A line after the rules says how many rule cards are
  waiting to be checked and how many are closed, and how to find them.
- A placeholder line the pack names (`- (none yet …)`) takes no status.
- "What needs checking" runs newest `created_at` first. It used
  `updated_at`, which on migrated cards is the migration's clock.
- Nothing in his file changes, and the round trip is unaffected.

Why: on Sputnik's memory the Rules section was about 3,500 tokens, 25 of its
entries proposals from August that his own file labels "do not rely on". His
protocol reads city rules only as needed, not every wake. Showing confirmed
rules only brings the section to about 950 tokens.

**Known gap, for the write half:** `done` is the nearest status to
"retracted", but recall leaves `done` cards out. A retraction exists so a
false belief isn't proposed again, so it should be findable. See W7.

### 5.3 Round trip (the most important test)

Join each file's current cards in order. Every original file must be
recovered **byte for byte**, including its line endings (CRLF or LF,
whichever the source used) and whether it ends with a newline. If one byte
differs, the migration fails. (v0.2: v0.1 allowed end-of-line differences,
and the rebuilt files came back LF-only.) Cards closed with the reason
`removed from source file` or `re-cut into keyed pieces` are left out of
the rebuild; otherwise a file would hold its text twice.

### 5.4 Re-cut after every file write

**The files stay the source** (for good, since 2026-10-05; v0.2 said "until
the write half lands"). The agent writes files. After each file write, the
harness cuts it into cards again. Logs and resident files are matched by
key (§5.1a). The other kinds are matched by `origin` and text: same IDs for
unchanged entries.

When a write both removes or inserts entries and edits others, the re-cut
runs in two passes. Removals and insertions run first. Edits run second.
If an edited entry can't be matched, its old card is marked removed and a
new card is made. Nothing is silently reassigned.

---

## 6. The wake card

One tool, `read_wake_card`, replaces the whole-file reads at the start of a
wake. Seven sections, always in this order, always present (write "none" when
empty). The table is the card as built at Sputnik `f9ec1d4` (2026-10-07):

| # | Section | Contents | Budget |
|---|---|---|---|
| 1 | **Who I am** | identity and governance, whole | not trimmed, counted in the whole-card budget |
| 2 | **What I was doing** | sections of the newest log (see "One wake back" below); `live` goals | 13,000 bytes |
| 3 | **What I owe** | the Due list of the newest log, as written; then `live` commitments, oldest first | 1,600 bytes |
| 4 | **Open threads (index)** | one line for each `live` thread: id, title, place and resident tags. A thread that doesn't fit is named by id | 4,800 bytes |
| 5 | **Rules** | `live` rule cards. Rules waiting to be checked are counted, not shown | 2,400 bytes |
| 6 | **What needs checking** | cards with status `recheck`; cards whose `supersedes` chain changed in the last wake | 1,200 bytes |
| 7 | **What's here** | `live` threads and relationships whose tags match where the agent is now and who is present (passed in as tags) | 400 bytes |

There was an eighth section, Decisions, built from the continuity file.
That file was retired on 2026-10-03 and the section went with it. `decision`
stays a valid card kind, so old cards still load.

Sections 2 to 7 add to 23,400 bytes. Identity and governance are about
18,300 bytes today, so the card is about 41,700 bytes at most, inside the
44,000 total. Measured on his memory on 2026-10-07: 37.8 KB whole, section 2
at 10.5 KB.
A test in Sputnik fails if identity plus the section budgets could exceed
one client view. Section 7 is empty in practice: the protocol reads the
card before it knows where the agent is, and recalls by place and person
in the next step. Section 7 shows `current` cards only.

**One wake back** (built 2026-10-07). The agent wakes with no memory of the
last wake, and the wake card is the first thing he reads. From the newest
log, section 2 shows:

1. the log's first section (the four lists) and its plan section, both
   whole, when the log has both. Neither is dropped for size;
2. the Observations section too, if the three together fit a setting
   (`wake_log_bytes`, 5,000 bytes of card text);
3. in the order they have in the log, under the log's title line once.

Which headings these are is three patterns in config (`log_first_heading`,
`log_observations_heading`, `plan_heading`). A log without a first-section
heading is shown as before: its plan section, or the fallback below. Section
3 opens with the Due list from the same first section, as written; until
commitment cards exist nothing else feeds it. The Due list therefore
appears twice on the card, in place and under "What I owe".

Two things for whoever builds on this. **What the card shows is an
example.** The agent tends to copy the shape of a list it is shown, so a
definition changed in the protocol may not change what is written while the
card still shows the old shape. **A list that says "none" is shown back as
the list.** Both are design notes from early use, not measured results.

- Budgets are in config. The total for the whole card is **44,000 bytes**
  (about 11,000 tokens), including identity and governance (Audrie,
  2026-10-03). Measured on 2026-10-04 at Sputnik `376c5d2`: the whole
  card is 34,027 bytes, including about 18,300 for identity and
  governance. One client view holds about 46,000 bytes. The budget comes
  from fitting the whole card in one client view.
- **Section 2 was raised from 6,400 to 8,000 bytes, then to 10,000, on
  2026-10-04** (Audrie), **and to 13,000 on 2026-10-07.** It holds the
  newest log's sections and the goals together. At 6,400 the largest goal
  card was left out; at 8,000, after one real wake added goals, two cards
  were. The rise to 13,000 made room for the log sections; a test checks
  that every goal card shown before is still shown with them at their
  full size.
- **Harness budgets are in bytes of UTF-8 text.** The harness can count
  bytes exactly, and a byte count is the same for every model. A token
  count depends on the model's tokenizer. Where a token figure stands
  beside a byte figure it is an estimate at four bytes a token, and it is
  low for text that isn't English. The code counts bytes since Sputnik
  `76be220`.
- **If a section doesn't fit, return the highest-ranked cards that do, and
  say how many were left out and how to recall them.** Never cut a card in
  half. If the whole card is still over 44,000 bytes, whole cards are
  dropped from the last section first; identity and governance are never
  trimmed.
- **Which log is newest**: the highest wake number in the log's filename,
  not `updated_at`. Re-cutting an old log moves its `updated_at`.
- **A log with no first-section heading** shows its title line and the
  piece whose heading says "plan next". If no piece has such a heading, it
  shows the log's header piece and the labels of its other pieces. A log
  that was never cut (one card, no key) is offered whole, and is left out
  with a notice if it doesn't fit.

---

## 7. Recall

`recall(tags=[...], text=None, kinds=None, limit=10, history=False)`:
- Returns the best-matching `live` cards (and `recheck`, marked), plus: what
  was searched, how many matched, how many were left out.
- **Current state first, history in a share** (built 2026-10-07). Matches
  are split by role (§5.1a). `current` cards are fitted first, whole, best
  match first. `history` cards are then fitted whole into a reserved share
  of the budget (`recall_history_bytes`, 6,000 of the 16,000); among history
  cards that match equally, the newest comes first. The share is reserved:
  when at least one history card matches, current cards get the budget less
  that share, so large current cards cannot leave history with nothing.
  When none matches, current cards may use it all. `history=True` gives
  history the whole budget.
- **The whole answer has its own limit** (`recall_answer_bytes`, 24,000
  bytes of the answer as the harness returns it, card text included). The
  first build of the lists below counted only card text against the budget,
  and the answer the agent received doubled (a recall of his home place:
  28.9 KB to 55.6 KB). When the answer would be over the limit the lists
  give way, in this order: `same_file`, `people`, `left_out_cards`. Card
  text is never dropped to make room for a list.
  - `left_out_cards`: at most 12 entries, best match first, each with id,
    kind, role, label and size; `left_out_counts` gives the totals by kind
    and by role.
  - `same_file`: for a returned piece of a log or a resident file, the
    other live pieces of that file, as id, label and size; at most eight a
    file.
  - `people`: when a `resident:` tag is in the query and that resident's
    `current` cards were not returned, they are listed the same way.
  - An empty list is left out of the answer.
  Measured on his memory on 2026-10-07: five recalls came back at 16.4 to
  23.1 KB whole.
- **A recall can still cost more than the file it replaces.** While goals
  and threads are large unsplit cards, a recall about one person returns
  those cards and its own metadata as well as the person's card, and can be
  many times the size of that person's file read directly. The sizes are
  measured again after goals and threads become small files (§8).
- Ranking v0: number of matching tags, then `weight`, then kind, then
  recency. No embeddings in v0.
  - Kind: among cards that match equally well, `relationship`, `thread`,
    `commitment` and `handover` cards come first and `log` cards last
    (Audrie, 2026-10-04). A mission log runs to 10,000 bytes or more. In a
    test wake a recall by place and resident returned one log, which used
    the budget, and left out the 2,358-byte card about the resident asked
    for.
  - Recency: `log` cards by the wake number in their filename, other cards
    by `updated_at`. Re-cutting an old log moves its `updated_at`.
- Per-call budget in config (16,000 bytes, about 4,000 tokens). **Over budget
  returns what fits, whole cards only, best match first,** and names the
  cards left out by id, kind, role, label and size (the first twelve, with a
  count of the rest) so one can be read with `read_card`. A card with no
  title is named by its first line
  (2026-10-03: a mission log left out of a recall could not be told from
  any other card). No
  card is ever cut. It is refused only when not even the best match fits.
  (Changed 2026-10-01: v0 refused the whole call. In the first test wake on
  cards, `recall(tags=["place:1146"])` matched 19,824 tokens against 4,000 and
  returned nothing, so the protocol's own Step 9 call failed at his home
  place.)
- **Reads never write.** Every recall is logged to
  `{memory}/cards/reads.jsonl` (time, wake, query, ids returned, session kind:
  `wake`, `sealed`, or `read-only`). Sealed and read-only lines are kept as
  evidence for later. Only `wake` lines count as the card having been read.
  Being read changes nothing on the card.
- `read_card(id)` returns one card, any status, with its history on request.

---

## 8. The write half, as redrawn on 2026-10-05

*Audrie's design. It replaces §8a and §9 below, which are kept as the record
of the earlier plan, and tickets W1 to W6 in §10.*

**In one paragraph.** The agent keeps writing files, and the files stay the
original. The tools cut every file at its headings into small labelled
cards and link the cards to each other. Anything he follows over time (a
resident, a place, a thing, a thread, a goal) has one short **current
state** that he keeps up to date, and a **history** of dated pieces behind
it. A recall returns the current state whole and the history mostly as
labels, so a search costs little and he chooses what else to open.

**What matters, in her order:**

1. **Linking.** A card that mentions a resident points at that resident's
   card, which points back at the wakes. Cards cut from one log point at
   each other.
2. **Labelling.** Every card says what it is in its label, built by the
   tool from facts it already has.
3. **Small pieces.** No card is big enough to crowd a recall.
4. **History without growth.** Current state is replaced, not added to.
   What it replaced is kept and is one call away.

**How each kind of file is cut:**

| File | Current state | History |
|---|---|---|
| Mission log (one a wake) | none: a log is history | one card per section |
| Resident file | the header and his impression | one per dated observation |
| Place | what the place is now | one per visit |
| Thing he wants to remember (new) | what it is, where, what he thinks of it now | one per encounter |
| Thread | where it stands now | one per dated update |
| Goal, project | the goal or project and its state | one per dated change |
| Lesson or rule | the rule itself | earlier wordings; a retraction with its reason |

**Definitions.** Much of the growth in his files was pattern-matching:
what he writes had never been defined, so each entry copied the shape of
the ones above it. A definition says what a thing is, what its parts are,
what it is not, and when it ends.

| Thing | What it is | Ends when |
|---|---|---|
| Ambition | the one standing aim, a sentence or two | never |
| Goal | a direction he holds, and how he pursues it. No steps, no finish line. A routine is a goal | he drops or replaces it |
| Project | a finite piece of work, usually under a goal: a target, steps, and one next step | the target is met or he abandons it; then it moves to a closed folder |
| Thread | a conversation or question with others that he may come back to. Not a record of a place visited once, and not work with steps | he closes it, with a date; it leaves the open list and stays findable |
| Observation | something he noticed and did not act on | |
| Lesson | a rule for how he acts, learned from something that happened | |

A definition fixes shape, not size. Growth is answered by closing and by
history kept behind the current state. Every slot that is defined gets
filled at every wake, so each one must allow "none".

**Build order** (three briefs; each is reviewed on a copy of his real
memory, pushed as a branch, passed by the hosted checks, then merged):

| Brief | What | State on 2026-10-08 |
|---|---|---|
| A | Logs and resident files cut small, keyed and labelled; recall by current state and history; the whole answer limited; the wake card shows one wake back | built and merged (§5.1a, §6, §7) |
| C | Goals and projects: the ambition stays where it is; one small file and one card for each goal and each project; a status line on each project; a finished project moved to a closed folder; small tools that change one thing | brief written, not built |
| B | Threads: one small file each; a tool to add to one and a tool to close one; the one-time split of the threads file. Finished visits go to an archive, byte for byte, before any split, so no thread file is made for them | not written |
| later | Lessons as small files; a file per remembered thing; a two-line summary in a log's header | not started |

Anything that moves text in his memory is done on the operator's decision
and visibly: text is moved, never reworded; the place it lands says the
operator moved it; he is told.

**What this settles from the earlier plan:**

- Cards do not become the source (W2). Nothing is generated back into a
  file, so the "printed file" question is gone.
- Id guessing is answered by keys for a file cut into pieces, and by one
  file per entry for the rest.
- The handover (§8a, W3) is the log's own plan section, shown at the next
  wake with the log's first section (§6).
- He replaces his own current state; earlier versions are kept. The
  operator moves, and marks the move.

**Still open:** a write that fails halfway where one call touches two
files; promises (what he owes someone has no card of its own, §8a W4); who
confirms a lesson and how a retracted one shows (W7); whether the map and
almanac become cards; the wake number after a failed save; whether a tag
that says "mentions" is enough, or some links need a stated reason.

### 8a. The handover card (earlier plan; not built)

At the end of every wake the agent writes one `handover` card:
- **Done:** what this wake did (short).
- **Unfinished:** what's in progress.
- **Check next time:** what to verify.
- **Owed:** new or changed commitments (as links).

`write_mission_log` asks for it. The next wake's section 2 opens with it.
This is the "seal" in `BUILD-SPEC.md` §7, in its first form.

---

## 9. Write tools (earlier plan; not built)

*Replaced by §8. The agent's write tools stay file tools. Each brief in §8
gives him small tools for its own kind of file, each changing one thing.
Kept because `supersede` and `set_status` describe what closing a thread
and replacing a current state have to do.*

| Tool | Does |
|---|---|
| `add_card(kind, text, title=None, links=[])` | New card. System sets every system field |
| `update_card(id, text=None, title=None, links=None)` | New version of a card. Old version stays in history |
| `set_status(id, status, reason)` | `done`, `recheck`, `live`. Reason required |
| `supersede(old_id, new_text)` | New card with `supersedes: old_id`; old gets `status: superseded` |
| `link(from_id, rel, to_id)` | Adds a link |

- The old whole-file writers (`update_open_threads`, `update_continuity`,
  `update_goals`, `append_lesson`) are removed from the wake protocol and
  kept only as operator repair tools.
- `GEMINI.md` changes are **proposed to Audrie as a diff**, never made by the
  builder. They must not add restraint or silence lines. "People first" still
  opens Act. (This rule stands under §8 too.)
- **Every tool call shown to the agent must be one he can make as written**:
  real tool name, named arguments, nothing required left out. A test checks
  the protocol and every message a tool prints against the real tool list.
  In 22 of his conversations nine calls were refused, seven of them one
  tool under six different argument names: his client shows him tool names
  and keeps each description in its own file. Since 2026-10-08 the harness
  accepts the names he uses and has a `help` tool that lists the tools and
  gives one tool's arguments with an example.

---

## 10. Tickets

**State on 2026-10-08.** R1 to R8 are built and Sputnik's wakes run on them.
In the template, R1 to R7 and the fixes to 2026-10-04 are on pushed
branches, not merged to `main`; everything built since (§5.1a, the changes
of 2026-10-07 in §6 and §7) is not in the template yet. W1 to W6 are
replaced by §8. W7 is still a proposal.

### Read half

| # | Ticket | Done when |
|---|---|---|
| R1 | **Card store.** `cards.jsonl` append-only, derived `index.json`, rebuild command. System fields set by the store | Tests: a model-set system field is refused; deleting `index.json` and rebuilding gives the same result; the append-only byte test |
| R2 | **Tag extractor + config.** Generic patterns in the template; city pack as a separate config file; the tag test set | Tag test set passes; fails once on a broken pattern |
| R3 | **Migration.** Cut each logical file into cards per §5.1; kind proposals per §5.2 | Runs on the made-up fixture and the private fixture; `kind-review.md` produced |
| R4 | **Round trip.** Views regenerated from cards | Every original file recovered exactly (§5.3), on both fixtures |
| R5 | **Re-cut on file write** (§5.4) | Tests: editing one entry in a file changes one card; other card IDs stay the same; an entry is edited while another is inserted above it, with removals and insertions first and edits second; if the edited entry cannot be matched, its old card is marked removed and a new card is made, with no silent reassignment |
| R6 | **`recall` and `read_card`** with budget and read log | Tests: over budget returns the cards that fit and names the rest; refused only if no card fits; a recall leaves `cards.jsonl` byte-identical |
| R7 | **`read_wake_card`**, seven sections, budgets in config | On the private fixture: the whole card fits 44,000 bytes; identity never trimmed; nothing cut mid-card |
| R8 | **Port to Sputnik + protocol diff.** Same code, city pack enabled; proposed `GEMINI.md` diff replacing the whole-file reads with `read_wake_card` + `recall` | Audrie reviews the diff. Then one read-only test wake (F0 method) shows the new orientation size |

### Write half (earlier plan; W1 to W6 replaced by §8)

| # | Ticket | Done when |
|---|---|---|
| W1 | **Write tools** (§9) | Tests for each; old versions stay in history |
| W2 | **Cards become the source.** Views generated after every write; direct file edits refused by the harness | Round trip still passes; a hand edit to a view is detected |
| W3 | **Handover card** in `write_mission_log` (§8) | The next wake card's section 2 shows it |
| W4 | **Commitments.** Kind confirmed by the agent in a wake; links `from` thread | A commitment appears in section 3 until `done` |
| W5 | **Protocol diff for writing**, proposed to Audrie | Reviewed before it lands |
| W7 | **One door for what he learns [proposal, not decided].** `append_lesson` and `propose_city_rule` become one write: a `rule` or `reflection` card, entered as `recheck`. The ladder from his rulebook is kept as card status: proposed = `recheck`, confirmed = `live` (by the operator, or after two verified outcomes in different wakes), retracted = a new status `retracted` that recall still returns, marked as false. `read_city_rules` and `propose_city_rule` leave the wake protocol and stay as operator repair tools. The template loses its city-named file: a rulebook is an environment pack matter | Audrie decides. Then: tests for the ladder (a `recheck` card can't be made `live` by the agent alone); the protocol diff is proposed, not made; his old file stays in his repo untouched |
| W6 | **Port to Sputnik** | One normal wake end to end; continuity probe in a sealed session scores no worse than before |

---

## 11. Open questions (for Audrie)

| # | Question | Default |
|---|---|---|
| Q1 | Section budgets (§6) | Decided 2026-10-03: 44,000 bytes (about 11,000 tokens) for the whole card, section budgets as in §6 |
| Q2 | Who confirms rule vs reflection | Sputnik, in a normal wake, told first in conversation |
| Q3 | Does `city_rules` merge into `rule` cards or stay a separate file | Merge, with a `source` of `self`. **Read side done 1 Oct** (§5.2a): his rulebook's entries are `rule` cards with status from their section. Write side is W7 |
| Q5 | One door for what he learns: retire `propose_city_rule` and the separate rulebook (W7)? | Yes, in the write half. Audrie leans yes (1 Oct); not yet decided |
| Q4 | Mission logs: keep five-per-wake reading anywhere? | No. **Done 2026-10-07**: the wake card shows the newest log's first and plan sections; older logs come by recall |
| Q6 | A short synopsis card for a long mission log, so one log can't take a whole recall (Sputnik's suggestion, 3 Oct) | **Answered another way, 2026-10-07**: a log is one card per section, so no single card is a whole log. A two-line summary in the log's header, in his words, is still wanted (§8, later) |
| Q7 | Is recall worth its cost to him once goals and threads are small files? | Re-measure the two baseline recalls of 2026-10-07 after briefs C and B (§7) |

---

*Drafted by Claude Opus 5.5 (POE desk, Claude Code) from conversation with
Audrie, 2026-09-30. v0.3 (2026-10-08) brings it level with what was built
from 4 to 8 October and with Audrie's design of 5 October. Ideas and
direction: Audrie. Reviewed by Audrie: pending.*
