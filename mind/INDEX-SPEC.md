# Memory cards and the associative index: build spec v0.2

*Stage 0 of `BUILD-SPEC.md`, in detail. Decision (Audrie, 2026-09-30):
**Option B**: memory becomes cards, and the cards are the truth. The old
memory files become generated views. Draft for review.*

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
and changes nothing about how the agent writes. The **write half** (W1–W6)
changes how the agent writes. Build and review the read half first.

---

## 1. What changes, in one paragraph

Today the agent's memory is a few big files, and every wake reads them whole
(~58,000 tokens for memory alone, growing every wake). After this build, each
memory is a **card**: one lesson, one thread, one goal, one log. Cards have a
kind, tags, a status and links. A wake starts by reading one **wake card**
built from the store, always the same five sections, always inside a token
budget. Everything else is **recalled** by tag when needed. The old files are
still produced, as read-only views, so humans and git history can read them.

---

## 2. The card

### 2.1 Fields

| Field | Set by | Meaning |
|---|---|---|
| `id` | system | Stable, never reused. Form: `<kind>-<number>`, e.g. `lesson-0107` |
| `kind` | system (migration) or agent (new card) | One of the kinds in §2.2 |
| `text` | agent | The card's content, in the agent's words. Markdown allowed |
| `title` | agent (optional) | Short label. For threads: the bold heading line |
| `tags` | system | Extracted by code from `text` and `title` (§4). Never written by the model |
| `status` | system, on agent request | `live`, `done`, `superseded`, `merged`, `recheck`, `structure` |
| `links` | agent or system | List of `{rel, to}`. `rel` in §2.3 |
| `created_at` | system | UTC time the card was first written |
| `updated_at` | system | UTC time of the last change |
| `wake` | system | Wake number the card was written or last changed in |
| `source` | system | Where the content came from: `self`, `operator`, `peer:<name>`, `world:<id>` |
| `channel` | system | How it arrived: `session`, `email`, `world`, `migration` |
| `weight` | system | Findability, 0.0–1.0. Starts at 1.0. Sleep lowers it. Never deletes |
| `origin` | system (migration only) | File and position the card was cut from |

`structure` marks a piece that holds only a file's shape, such as a heading
or a preface. It is kept so the file can be rebuilt byte for byte. It is
left out of the wake card and of recall. Built in Sputnik `773ff06`.

**Rule:** the model never sets `id`, `tags`, `created_at`, `updated_at`,
`wake`, `source`, `channel`, `weight` or `origin`. If a write tries to, refuse
it with a reason.

### 2.2 Kinds

| Kind | Means | Comes from today (logical name) |
|---|---|---|
| `goal` | What the agent is working towards | `goals` |
| `commitment` | A promise made to someone. Owed | nowhere clean yet (scattered) |
| `thread` | Something the agent **may** return to. **Not owed** | `open_threads` |
| `rule` | Short, practical, keep in mind | `lessons` (short entries), `city_rules` |
| `reflection` | The agent's thinking about what it saw | `lessons` (long entries) |
| `decision` | A settled choice and its reason | `continuity` |
| `relationship` | What the agent knows about someone | `residents` |
| `log` | One wake's record | `journal` (mission logs) |
| `handover` | What the next wake needs. One per wake | new |

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
- **Generated views:** the old files (`lessons`, `open_threads`, `goals`,
  `continuity`) are regenerated from cards after every write, with a header
  line: `<!-- Generated from cards. Do not edit. -->`. During the read half
  they stay the source (§5.4).
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
| `journal` | one card per file | `log` | `wake` from the file name |
| `residents` | one card per dossier file | `relationship` | `tags` include `resident:<id>` |

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

Generate the views from the cards. Every original file must be recovered
**byte for byte**, including its line endings (CRLF or LF, whichever the
source used) and whether it ends with a newline. If one byte differs, the
migration fails. (v0.2: v0.1 allowed end-of-line differences, and the views
came back LF-only; once cards are the source, that would change every file
in git.)

### 5.4 During the read half

Until the write half lands, **the files stay the source.** The agent keeps
writing files the old way. After each file write, the harness re-cuts that
file into cards (same IDs for unchanged entries: match by `origin` and
text). This keeps the read half safe to ship on its own.

When a write both removes or inserts entries and edits others, the re-cut
runs in two passes. Removals and insertions run first. Edits run second.
If an edited entry can't be matched, its old card is marked removed and a
new card is made. Nothing is silently reassigned.

---

## 6. The wake card

One tool, `read_wake_card`, replaces the whole-file reads at the start of a
wake. Eight sections, always in this order, always present (write "none" when
empty). The table is the card as built at Sputnik `5448e4f`:

| # | Section | Contents | Budget |
|---|---|---|---|
| 1 | **Who I am** | identity and governance, whole | not trimmed, counted in the whole-card budget |
| 2 | **What I was doing** | the last `handover` card; `live` goals | 1,600 tokens |
| 3 | **What I owe** | `live` commitments, oldest first | 400 tokens |
| 4 | **Open threads (index)** | one line for each `live` thread: id, title, place and resident tags. A thread that doesn't fit is named by id | 1,200 tokens |
| 5 | **Decisions** | `live` decision cards, in file order. Being retired with the continuity file (decided 2026-10-03) | 700 tokens |
| 6 | **Rules** | `live` rule cards. Rules waiting to be checked are counted, not shown | 600 tokens |
| 7 | **What needs checking** | cards with status `recheck`; cards whose `supersedes` chain changed in the last wake | 300 tokens |
| 8 | **What's here** | `live` threads and relationships whose tags match where the agent is now and who is present (passed in as tags) | 100 tokens |

Sections 2 to 8 add to 4,900 tokens. Identity and governance are about
4,560 today, so the card is about 9,500 at most, inside the 11,000 total.
A test in Sputnik fails if identity plus the section budgets could exceed
one client view. Section 8 is empty in practice: the protocol reads the
card before it knows where the agent is, and recalls by place and person
in the next step.

- Budgets are in config. The total for the whole card is **11,000 tokens**,
  including identity and governance (Audrie, 2026-10-03). Measured on
  2026-10-03 at Sputnik `5448e4f`: the whole card is about 9,300 tokens,
  including about 4,560 for identity and governance. One client view holds
  about 46,000 bytes, roughly 11,500 tokens. The budget comes from fitting
  the whole card in one client view.
- Count tokens as characters ÷ 4 unless a real tokenizer is available.
- **If a section doesn't fit, return the highest-ranked cards that do, and
  say how many were left out and how to recall them.** Never cut a card in
  half.
- Before a handover card exists (first run), section 2 uses the newest `log`
  card's last section.

---

## 7. Recall

`recall(tags=[...], text=None, kinds=None, limit=10)`:
- Returns the best-matching `live` cards (and `recheck`, marked), plus: what
  was searched, how many matched, how many were left out.
- Ranking v0: number of matching tags, then `weight`, then newest
  `updated_at`. No embeddings in v0.
- Per-call budget in config (proposed 4,000 tokens). **Over budget
  returns what fits, whole cards only, best match first,** and names every
  card left out by id, kind, title, size and source file so it can be read
  with `read_card`. A card with no title is named by its first line
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

## 8. The handover card (write half)

At the end of every wake the agent writes one `handover` card:
- **Done:** what this wake did (short).
- **Unfinished:** what's in progress.
- **Check next time:** what to verify.
- **Owed:** new or changed commitments (as links).

`write_mission_log` asks for it. The next wake's section 2 opens with it.
This is the "seal" in `BUILD-SPEC.md` §7, in its first form.

---

## 9. Write tools (write half)

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
  opens Act.

---

## 10. Tickets

### Read half

| # | Ticket | Done when |
|---|---|---|
| R1 | **Card store.** `cards.jsonl` append-only, derived `index.json`, rebuild command. System fields set by the store | Tests: a model-set system field is refused; deleting `index.json` and rebuilding gives the same result; the append-only byte test |
| R2 | **Tag extractor + config.** Generic patterns in the template; city pack as a separate config file; the tag test set | Tag test set passes; fails once on a broken pattern |
| R3 | **Migration.** Cut each logical file into cards per §5.1; kind proposals per §5.2 | Runs on the made-up fixture and the private fixture; `kind-review.md` produced |
| R4 | **Round trip.** Views regenerated from cards | Every original file recovered exactly (§5.3), on both fixtures |
| R5 | **Re-cut on file write** (§5.4) | Tests: editing one entry in a file changes one card; other card IDs stay the same; an entry is edited while another is inserted above it, with removals and insertions first and edits second; if the edited entry cannot be matched, its old card is marked removed and a new card is made, with no silent reassignment |
| R6 | **`recall` and `read_card`** with budget and read log | Tests: over budget returns the cards that fit and names the rest; refused only if no card fits; a recall leaves `cards.jsonl` byte-identical |
| R7 | **`read_wake_card`**, eight sections, budgets in config | On the private fixture: the whole card fits 11,000 tokens; identity never trimmed; nothing cut mid-card |
| R8 | **Port to Sputnik + protocol diff.** Same code, city pack enabled; proposed `GEMINI.md` diff replacing the whole-file reads with `read_wake_card` + `recall` | Audrie reviews the diff. Then one read-only test wake (F0 method) shows the new orientation size |

### Write half (after the read half is reviewed)

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
| Q1 | Section budgets (§6) | Decided 2026-10-03: 11,000 for the whole card, section budgets as in §6 |
| Q2 | Who confirms rule vs reflection | Sputnik, in a normal wake, told first in conversation |
| Q3 | Does `city_rules` merge into `rule` cards or stay a separate file | Merge, with a `source` of `self`. **Read side done 1 Oct** (§5.2a): his rulebook's entries are `rule` cards with status from their section. Write side is W7 |
| Q5 | One door for what he learns: retire `propose_city_rule` and the separate rulebook (W7)? | Yes, in the write half. Audrie leans yes (1 Oct); not yet decided |
| Q4 | Mission logs: keep five-per-wake reading anywhere? | No. Handover + recall replace it |
| Q6 | A short synopsis card for a long mission log, so one log can't take a whole recall (Sputnik's suggestion, 3 Oct) | Yes, as a sleep step. Not designed yet |

---

*Drafted by Claude Opus 5.5 (POE desk, Claude Code) from conversation with
Audrie, 2026-09-30. Ideas and direction: Audrie. Reviewed by Audrie: pending.*
