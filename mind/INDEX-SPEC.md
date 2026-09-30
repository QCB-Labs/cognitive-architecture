# Memory cards and the associative index: build spec v0.1

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
| `status` | system, on agent request | `live`, `done`, `superseded`, `merged`, `recheck` |
| `links` | agent or system | List of `{rel, to}`. `rel` in §2.3 |
| `created_at` | system | UTC time the card was first written |
| `updated_at` | system | UTC time of the last change |
| `wake` | system | Wake number the card was written or last changed in |
| `source` | system | Where the content came from: `self`, `operator`, `peer:<name>`, `world:<id>` |
| `channel` | system | How it arrived: `session`, `email`, `world`, `migration` |
| `weight` | system | Findability, 0.0–1.0. Starts at 1.0. Sleep lowers it. Never deletes |
| `origin` | system (migration only) | File and position the card was cut from |

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
| `resident:188` | `#188` next to a name or the word resident; `(#188)` |
| `place:1207` | `Place 1207`, `Places 1204 & 1205`, `[195]` in a routing context |
| `continent:1201` | `Continent #1201` |
| `note:25540` | `Note #25540` |
| `thing:4741` | `Thing #4741` |
| `post:7164` | `Post #7164` |
| `kind-id:39` | `Kind #39` |
| `name:glimmerbell` | a resident handle listed in `residents/index` |

### 4.2 Rules

- A pattern that matches ambiguously (`#188` with no context) gets the
  generic tag `ref:188`. Don't guess the type.
- Tags are lower case.
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
| `city_rules` | each top-level bullet or `##` heading | `rule` | |
| `open_threads` | each top-level `- **...**` item | `thread` | The bold line is `title`. Items under `## Resolved threads` get `status: done` |
| `goals` | each goal heading or top-level item | `goal` | Keep the file's order |
| `continuity` | each `##`/`###` section | `decision` | |
| `journal` | one card per file | `log` | `wake` from the file name |
| `residents` | one card per dossier file | `relationship` | `tags` include `resident:<id>` |

If a file doesn't fit its rule (no headings, mixed formats), **stop and
report** with examples. Don't invent a rule.

### 5.2 Rule or reflection

Code proposes, a human or the agent confirms:
- Proposed `rule`: under 400 characters and no `###` subheadings.
- Proposed `reflection`: anything else.
- Every proposal is written to `{memory}/cards/kind-review.md` for
  confirmation. Until confirmed, the card carries status `recheck`.

### 5.3 Round trip (the most important test)

Generate the views from the cards. The text of every original file must be
recoverable **exactly**, apart from whitespace at the ends of lines. If one
character of the agent's words is lost or changed, the migration fails.

### 5.4 During the read half

Until the write half lands, **the files stay the source.** The agent keeps
writing files the old way. After each file write, the harness re-cuts that
file into cards (same IDs for unchanged entries: match by `origin` and
text). This keeps the read half safe to ship on its own.

---

## 6. The wake card

One tool, `read_wake_card`, replaces the whole-file reads at the start of a
wake. Five sections, always in this order, always present (write "none" when
empty):

| # | Section | Contents | Budget |
|---|---|---|---|
| 1 | **Who I am** | identity and governance, whole | not trimmed, not counted against the rest |
| 2 | **What I was doing** | the last `handover` card; `live` goals | 3,000 tokens |
| 3 | **What I owe** | `live` commitments, oldest first | 2,000 tokens |
| 4 | **What needs checking** | cards with status `recheck`; cards whose `supersedes` chain changed in the last wake | 2,000 tokens |
| 5 | **What's here** | `live` threads and relationships whose tags match where the agent is now and who is present (passed in as tags) | 4,000 tokens |

- Budgets are in config. Proposed total for sections 2–5: **11,000 tokens**.
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
- Per-call budget in config (proposed 4,000 tokens). **Over budget is
  refused, not truncated:** return the count and ask for a narrower recall.
- **Reads never write.** Every recall is logged to
  `{memory}/cards/reads.jsonl` (time, wake, query, ids returned). Being read
  changes nothing on the card.
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
| R5 | **Re-cut on file write** (§5.4) | Tests: editing one entry in a file changes one card; other card IDs stay the same |
| R6 | **`recall` and `read_card`** with budget and read log | Tests: over budget is refused; a recall leaves `cards.jsonl` byte-identical |
| R7 | **`read_wake_card`**, five sections, budgets in config | On the private fixture: sections 2–5 fit 11,000 tokens; identity never trimmed; nothing cut mid-card |
| R8 | **Port to Sputnik + protocol diff.** Same code, city pack enabled; proposed `GEMINI.md` diff replacing the whole-file reads with `read_wake_card` + `recall` | Audrie reviews the diff. Then one read-only test wake (F0 method) shows the new orientation size |

### Write half (after the read half is reviewed)

| # | Ticket | Done when |
|---|---|---|
| W1 | **Write tools** (§9) | Tests for each; old versions stay in history |
| W2 | **Cards become the source.** Views generated after every write; direct file edits refused by the harness | Round trip still passes; a hand edit to a view is detected |
| W3 | **Handover card** in `write_mission_log` (§8) | The next wake card's section 2 shows it |
| W4 | **Commitments.** Kind confirmed by the agent in a wake; links `from` thread | A commitment appears in section 3 until `done` |
| W5 | **Protocol diff for writing**, proposed to Audrie | Reviewed before it lands |
| W6 | **Port to Sputnik** | One normal wake end to end; continuity probe in a sealed session scores no worse than before |

---

## 11. Open questions (for Audrie)

| # | Question | Default |
|---|---|---|
| Q1 | Section budgets (§6) | 3k / 2k / 2k / 4k = 11k |
| Q2 | Who confirms rule vs reflection | Sputnik, in a normal wake, told first in conversation |
| Q3 | Does `city_rules` merge into `rule` cards or stay a separate file | Merge, with a `source` of `self` |
| Q4 | Mission logs: keep five-per-wake reading anywhere? | No. Handover + recall replace it |

---

*Drafted by Claude Opus 5.5 (POE desk, Claude Code) from conversation with
Audrie, 2026-09-30. Ideas and direction: Audrie. Reviewed by Audrie: pending.*
