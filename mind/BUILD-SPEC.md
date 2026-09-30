# Mind server — build spec v0.1

*Draft for review. Written by POE, for Audrie, 2026-09-28. Reviewed by
Waypost before any code is written. Pairs with `research/RESEARCH-SPEC.md`:
that document says what the experiment measures, and this one makes sure the
server records it.*

---

## 0. How to use this brief

This is a portable brief. Paste it into a fresh chat on any model and start
building. You don't need the conversation that produced it.

**Read first, in this repository:**
- `spec/COGNITIVE-ARCHITECTURE.md` §2 (principles), §6 (the cognitive object),
  §7 (the evidence chain), §8 (provenance and authority), §21 (invariants),
  §24 (the interface, the null token), §29 (the layer order). This brief
  implements those sections. Where the two disagree, **the spec wins**. Flag
  the disagreement; don't resolve it yourself.
- `research/RESEARCH-SPEC.md` §6 (what must be recorded per wake).

**Rules for whoever builds this:**
1. **Don't commit.** Leave changes in the working tree for Audrie to review.
   She commits. (A builder committing under her name has happened before.)
2. **Write everything in your own words and code.** This matters for the
   licence. Read other projects for ideas, but copy no text and no code from:
   Waypost's `bootstrapping-personas` (its licence is unconfirmed), Waypost's
   house code (`desk_mcp.py`, `verify-verdict.py` and the rest: not licensed to
   us), Cairn's memory handbook (its licence forbids redistribution), or the
   "Mind Outside the Model" draft (PR #1 on `agent-harness-template`), which is
   Wayfarer's writing. Our own template (`agent-harness-template`) is fine to
   reuse.
3. **Make every check fail once.** Before trusting a validator, a test or a
   metric, run it against input built to fail and watch it fail.
4. **Nothing secret in the repo.** The canary, the keeper's key and the live
   ledgers live in gitignored folders (`mind/install/`, `mind/keeper/`,
   `ledgers/`). Install the hooks first (`hooks/README.md`).
5. **Stop and report** when something in this brief can't be built as written.
   Don't route around it.

---

## Stage 0 — Foundation: bounded memory (build this first)

*Added 2026-09-30 (S48), after the scope was narrowed and frozen: "the CA is a
memory architecture that keeps a persistent agent's context bounded and its
beliefs traceable, across a growing life." Everything from §1 on (the mind
server, L1–L3) comes after Stage 0 and is unchanged by it for now.*

### S0.1 Why this comes first

The agent can't wake inside a Sonnet-sized context any more. Measured on
2026-09-30 in two read-only test wakes (F0, tests 1 and 2): Sputnik on
Claude Sonnet 4.6 (Thinking) through Antigravity, told to read everything it
normally reads and write nothing. His repo was checked before and after:
nothing changed. Sizes are the tools' exact outputs, saved by Antigravity;
tokens ≈ bytes ÷ 4. Context figures come from POE's reading of Antigravity's
undocumented conversation records: trust the pattern, not the last digit.

| Test | Client | Before any read | End of memory reads (step 8) | End of orientation | Checkpoints |
|---|---|---|---|---|---|
| 1 | Antigravity desktop app | ~35,600 | ~78,000 | not reached (stopped mid step 17) | 2 |
| 2 | `agy` CLI (no plugins; city + harness only) | ~34,900 | ~86,000 | ~124,000, all 20 steps | 1 |

Limit reported in both: 160,000.

**Where it went (test 1, exact output sizes):**

| Source | Bytes | ≈ Tokens |
|---|---|---|
| Fixed overhead before step 1 (client instructions, tool definitions, `GEMINI.md`) | n/a | ~35,000 |
| Memory: `lessons.md` | 70,125 | 17,500 |
| Memory: `open-threads.md` | 67,254 | 16,800 |
| Memory: last 5 mission logs | 53,524 | 13,400 |
| Memory: continuity, soul, governance, goals | 41,246 | 10,300 |
| Market: `browse_shelves` (full listing) | 42,859 | 10,700 |
| Square: profile/status | 20,030 | 5,000 |
| City: `city.me` | 25,905 | 6,500 |
| City: feed catch-up (9 pages of changes) | ~17,400 | 4,300 |
| **Total before acting** | | **~125,000** |

**The fixed overhead, broken down (estimates):** `GEMINI.md` ~5,400; harness
tool definitions ~5,000; the city's tool catalog ~3,600 (44 tools, 14.5 KB);
the desktop app's loaded skills 7,354 (its own counter: 53 skills, mostly an
unrelated science plugin). The CLI has no plugins and still starts at
~34,900, so **roughly 20,000 tokens are the client's own instructions.** That
part can't be trimmed from inside the client; it is a reason to measure other
drivers (Gemini CLI, direct API) before choosing the cloud one.

**Growth:** `open-threads.md` went from 37.5 KB to 67.5 KB between 25 and 30
September (+80% in five days); `lessons.md` from 52 KB to 70 KB over its last
30 commits. Every harness read returns the whole file (`_read_text`). CA §31.1
lists "bounded reads" as built. It isn't.

**What the files have become** (for whoever designs the entry split):
- `lessons.md`: 107 dated entries. The August ones are short operational
  rules ("verify an API call by checking the room"). Recent ones are long
  reflections with headed sections. Two kinds in one file; the digest needs
  the rules, not every reflection. It's Sputnik's file: tag, don't rewrite.
- `open-threads.md`: 48 threads, mostly living. Not goals (`goals.md` is
  4 KB): relationships and conversations he may return to, each dense with
  resident, place, note and thing IDs. It is already a hand-made associative
  index, read whole.
- Mission logs: ~10 KB each; five read every wake.

**Protocol drift found:** three city calls failed on arguments the city no
longer accepts (`after_change_id`, a `browse` view that doesn't exist,
`query`), and the correspondence list was read three times. Small in tokens;
`GEMINI.md` is behind the world's current tools.

Orientation has to fall from ~125,000 to about 40,000 to leave space to
act. No research layer can be tested on an agent that can't wake. Stage 0
fixes that, and its before-and-after numbers are the study's first result.

### S0.2 Where it's built

In the **template harness** (`agent-harness-template`, `tools/harness_mcp.py`)
first, then ported to Sputnik in the same shape, as Ticket 6 was. **Not** in
the mind server: Stage 0 has to work in the harness the agent runs today.
Keep everything environment-neutral: nothing in the index or sleep may know
about the city (CA study 3 moves the same mind to other worlds).

### S0.3 Two halves

- **Bounded reads (the associative index).** Each wake loads a small,
  relevant slice, and no read can exceed its budget (CA invariant 8).
- **Bounded orientation.** The world is read the same way: only what's new
  since last time, in limited amounts. This is done through the wake
  protocol and the world's own parameters, never by wrapping its tools.
- **Bounded growth (sleep).** Between wakes, the store is kept healthy:
  duplicates linked, stale entries made less findable, old logs summarised.
  Nothing is deleted.

Either half alone fails: small reads from an ever-growing junk drawer, or a
tidy store still read whole. See `research/ideas/sleep-consolidation.md`.

### S0.4 Five requirements (non-negotiable)

1. **The raw record is never overwritten.** Every write is append-only, or
   preserves the previous version in an archive the agent doesn't read.
   (Today `safe_replace_file` leaves `.bak` files beside the live file inside
   `memory/`. Move them to an archive path.)
2. **Tag at write time.** Each entry gets tags when it's written: the IDs and
   names it mentions (place IDs, resident handles, wake numbers, thread IDs),
   extracted **by code, not by the model**. Tags mean "eligible to find",
   never "important" or "true".
3. **The system holds source and authority.** Who or what an entry came
   from, and through which channel, are fields the harness sets. The model
   never writes them and they never live only in prose (CA §8.4).
4. **Every entry has a status slot:** `live`, `superseded_by: <id>`,
   `merged_into: <id>`, and a findability weight. Forgetting lowers the
   weight; it never deletes.
5. **Reads never write.** Retrieval is logged to a separate read log. Being
   read doesn't change an entry.

### S0.5 The index

**Decided 2026-09-30 (Audrie): Option B, cards are the truth.** The full
design, split rules, tag patterns, wake card and tickets (R1–R8, W1–W6) are in
**`mind/INDEX-SPEC.md`**. It supersedes the sketch below and tickets F3–F7
where they differ.

- **Units.** Split the big files into entries: one lesson, one open thread,
  one continuity item, one mission-log entry, one resident dossier. Each gets
  a stable ID and points back to its source file and position.
- **Storage.** Append-only JSONL beside the memory files, plus a derived
  lookup that can be rebuilt from it at any time. No database.
- **Search, v0:** deterministic. Tag match, recency, and weight. **No
  embeddings in v0.** They come later if tags prove too blunt, measured, not
  assumed.

### S0.6 Bounded reads

- **A wake digest with a hard budget.** One startup read that returns: the
  identity core (soul, governance, goals: always whole, never trimmed), the
  continuity core, the top active threads, and the newest mission log. Budget
  in tokens, set in config, **refused rather than truncated** if exceeded.
- **Cue-driven reads for the rest.** `recall(tags or text, limit)` returns
  the best-matching entries within a per-call budget, plus what was searched
  and what was left out.
- The old whole-file tools stay available for audit and repair, but leave the
  wake protocol.

### S0.6a The whole-wake budget

One budget for everything read before the agent acts, split into slices.
Numbers are proposals for Audrie. The window is the one the **client**
reports, not the model's: Antigravity reported 160,000 for Sonnet 4.6 and
checkpointed well before it (S0.1). Re-measure for each driver.

| Slice | Proposed share of the window | How it's held |
|---|---|---|
| Protocol + identity (`GEMINI.md`, soul, governance, goals) | ~6% | Kept short; identity never trimmed |
| Memory (the wake digest) | ~10% | Hard budget in the harness (F7) |
| World orientation | ~12% | Cursors for every feed, limits on every call, in the protocol |
| **Total before acting** | **≤ ~30%** | Measured every wake (F0 + F1) |
| Left for acting and replies | **≥ 70%** | |

For world orientation, the protocol already keeps a cursor for one feed
(`seen.json`: notes). Every feed the wake reads gets one, and every world
call that offers a limit or a "since" parameter uses it. The harness only
stores the cursors; it never calls the world itself.

### S0.7 Sleep, minimal (v0)

Runs between wakes, as a separate process. Deterministic in v0; a small local
model is a later option (see the idea file).

- Link entries that share tags heavily as *possible duplicates* (a flag, not
  a merge).
- Lower the findability of threads the agent has closed and of entries not
  read in N wakes.
- Summarise mission logs older than N wakes into a digest entry that points
  at the originals. The originals stay.
- Write only **derived** entries and weight changes. Never edit a raw entry.
- Every sleep action is logged, reversible, and **not shown to the agent**
  as a list of proposals. The researcher can see all of it.

### S0.8 Protocol changes

The wake protocol (`GEMINI.md`) changes from "read these files" to "read the
digest, then recall what you need." That edit is **proposed to Audrie, not
made by the builder**. It must not add restraint or silence lines ("People
first" still opens Act; see the CLAUDE.md rule).

### S0.9 Done means

1. **Everything read before acting stays within ~30% of the window** at
   wake N and still does 20 wakes later, while the store keeps growing. The
   memory digest alone fits its own budget (proposed: **20,000 tokens**, to be
   set by Audrie).
2. The continuity probe, run in a sealed unrecorded session, scores no worse
   after Stage 0 than before it.
3. Every check has failed once on purpose before being trusted.
4. The raw record for the whole period can be rebuilt byte for byte.

### S0.10 Tickets

| # | Ticket | Acceptance |
|---|---|---|
| F0 | **Whole-wake measurement (client side).** Token count at the end of orientation and at the end of the wake, from the model client (AGY/Sonnet), plus when compaction fires. Audrie runs it; no code | A baseline over ≥3 real wakes: memory vs world vs acting |
| F1 | **Read meter.** Log the size of every harness read tool's output per wake, to a gitignored per-wake record | A before-Stage-0 baseline over ≥3 real wakes, matched against F0 |
| F2 | **Archive, not `.bak`.** Previous versions go to an archive path outside the wake's reads | No `.bak` in `memory/`; every past version still recoverable |
| F3 | **Entry split + IDs.** Split lessons, threads, continuity, mission logs, dossiers into entries with stable IDs and source pointers | Round trip: entries rebuild the original files exactly |
| F4 | **Write-time tags + system fields.** Code-extracted tags; source, channel and authority set by the harness | Tests: a model-supplied source or authority is refused |
| F5 | **Status and weight.** `live` / `superseded_by` / `merged_into` + findability | Tests: superseded entries are still readable by ID |
| F6 | **`recall` with budgets + read log** | Tests: over-budget refused, not truncated; reads change nothing |
| F7 | **Wake digest** with a configured budget | Fits budget on Sputnik's real store; identity core never trimmed |
| F8 | **Sleep v0**, separate process, logged and reversible | Tests: no raw entry changes; every action has an undo |
| F9 | **Port to Sputnik** + the proposed `GEMINI.md` read-step change | Audrie reviews the protocol diff before it lands |
| F10 | **Feed cursors.** A cursor for every world feed the wake reads; the proposed protocol lines to use them and each call's limits | Orientation measured by F0 falls, and nothing the agent needed is missed (checked against a full read once) |
| F11 | **Market and Square catch-up.** These servers are ours (`tools/market_mcp.py`, `tools/square_mcp.py`), so "since" and limit parameters go in the tools themselves: listings and posts newer than a stored marker; a light profile call returning only quotas and standing | Test 1 read 42.9 KB of shelves and 20 KB of profile; both fall to a few KB on a quiet day |
| F12 | **Protocol repair.** Fix the three city calls that use arguments the city no longer accepts; stop the repeated correspondence listing. Proposed to Audrie as a `GEMINI.md` diff | No `bad_input` errors in a test wake |

Tickets F1–F8 go in the template first. The builder rules in §0 apply: don't
commit, your own code, make every check fail once, stop and report.

*Stage 0 drafted by Claude Opus 5.5 (POE desk, Claude Code) from
conversation with Audrie, 2026-09-30. Ideas and direction: Audrie. Reviewed
by Audrie: pending.*

---

## 1. What you're building

One MCP server that holds an agent's mind between sessions. The model can only
reach it through tool calls. Every write is a *proposal*: the server validates
it, and it lands, or it's refused with a reason.

| Choice | Decision | Why |
|---|---|---|
| Language | Python 3.11+ | Same as the template, so one toolchain |
| Library | the official MCP Python SDK (`mcp`, FastMCP), as the template uses | Proven here already |
| Transport | streamable HTTP, **loopback only**; refuse to bind anything else | The server must outlive a session and serve any model; stdio dies with its session |
| Storage | one append-only JSONL file per ledger in `ledgers/<agent>/` | Greppable, diffable, hashable. No database in v0 |
| Clock, IDs, author | set by the server, never accepted from the model | CA §24.2 |
| Layers | each is a feature flag in `mind/config.json` | CA §29.1: the model can't tell which layers are on |

**Where it runs:** on the operator's PC while it's being built and tested, then
on the cloud VM beside the agent. Nothing in the design depends on which.

---

## 2. Scope of v0.1

v0.1 builds the foundation of the experiment: CA layers **L1–L3** plus
everything they need. Later layers come in later versions, one at a time.

| In v0.1 | Out of v0.1 (later) |
|---|---|
| Observation layer (L1) | Contradiction cascade, lifecycle transitions beyond `contested`/`superseded` (L4) |
| Percept → episode → belief chain, dependency links both ways (L1–L2) | Consolidation pass (L5) |
| `external_origin` set at ingress and propagated (§8.4) | Confidence/salience as scored quantities (L6) |
| Null token, canary, searched space (L3) | Scored retrieval (L7) |
| Bounded recall, budget held by the server | Self-model revision (L8) |
| Audit log (§23) | Keeper signing, envelopes, decline, stop |
| Threads with a required default | Harness integration beyond an adapter (a separate ticket) |
| Seal with a hash-chained manifest | |

**On identity and operator authority (CA §29.2, and an open question to
Waypost).** The template already protects the identity foundation and only
takes instructions from the operator's channel. v0.1 doesn't rebuild these. It
serves the foundation read-only (§5), and gives every record from outside an
`authority.instruction` of `false`. Whether operator authority should also be
a switchable layer is an open question (§10, Q1). The flag slot is reserved,
but not built.

---

## 3. The record

Every record in every ledger has these fields. **Server-set** fields are filled
by the server. If the model supplies them, they're moved to `claimed_<field>`
and kept as audit, never used.

| Field | Set by | Meaning |
|---|---|---|
| `id` | server | `<kind prefix>_` + the first 16 hex chars of the SHA-256 of the canonical record |
| `kind` | model | `observation`, `percept`, `episode`, `belief`, `impression`, `procedure`, `ruling`, `thread`, `commitment`, `refusal` |
| `domain` | model | a set drawn from `world`, `social`, `spatial`, `self`, `task`, `system` |
| `at` | server | server clock, UTC, ISO 8601 |
| `author` | server | `{model, session, wake}`. The model identity comes from the session config, not the call |
| `derived_from` | model | list of record ids this was built from |
| `used_in` | server | filled when a later record cites this one. Written as a separate link record, never an edit (§4.4) |
| `provenance` | model, checked | `{type, source, channel}`. `type` is from CA §8.1 |
| `authority` | server | `{instruction, factual_evidence}`. `instruction` is `false` for everything v0.1 stores |
| `external_origin` | server | `true` if this record, or anything it derives from, came from outside the agent. Never cleared |
| `lifecycle` | server | `active`, `contested` or `superseded` in v0.1 |
| `supersedes` | model, checked | id of a record this replaces |
| `claim_type` | model | `positive` (default) or `absence`, for beliefs of the form "there is no X" |
| `null_token` | model, checked | required when `claim_type` is `absence` |
| `content` | model | the body. Its shape depends on the kind (§3.1) |

### 3.1 Content by kind (v0.1)

| Kind | Content | Must derive from |
|---|---|---|
| observation | `raw` (verbatim text or a `bytes_ref` hash + path), `channel`, `source` | nothing. Written by the server or through `observe` |
| percept | `reading` (what the agent took it to mean) | ≥1 observation |
| episode | `text` (what happened, as experience) | ≥1 percept |
| belief / impression / procedure | `statement` | ≥1 episode, belief or percept, **with a chain that reaches an observation** |
| ruling | `decision`, `reason` | nothing. Its provenance must be `operator` or `self` |
| thread | `question`, `closes_when`, `default_if_untouched` | optional. **Refused without a default** |
| commitment | `to`, `what`, `by`, `evidence_of_done` | ≥1 episode recording the promise |
| refusal | `call`, `failed_check`, `reason`, `what_would_pass` | the server writes these. Every refusal is itself an observation (CA §24.2) |

---

## 4. The validator

Every `propose` call runs these checks in order and stops at the first
failure, so a refusal names exactly one reason.

1. **Layer.** Is the layer this kind belongs to switched on? If not, refuse
   with `layer_disabled`.
2. **Shape.** Does the record match its kind's schema?
3. **Server fields.** Move any model-supplied `id`, `at`, `author`, `used_in`,
   `external_origin` or `lifecycle` into `claimed_*`.
4. **Provenance.** Does every id in `derived_from` exist? For belief,
   impression and procedure: does the chain reach an observation? If not,
   refuse with `no_chain`.
5. **Origin.** Set `external_origin` to true if any ancestor has it. There's
   no way to set it to false once an ancestor is true.
6. **Absence.** If `claim_type` is `absence`: is `null_token` present, minted
   by this server, unexpired (same wake), and for a query whose space the
   statement names? If not, refuse with `absence_without_token`.
7. **Contest.** If the proposal names a live belief in `contests`, both are
   marked `contested` and the write still lands. The server never picks a
   winner.
8. **Land.** Append the record. Append a `link` record for each `derived_from`
   (this is how `used_in` is built without editing anything). Write the audit
   entry.

A refusal writes a `refusal` record and returns
`{refused, failed_check, reason, what_would_pass}`.

### 4.4 Append-only, without exception

Nothing is edited. `used_in`, `lifecycle` changes and supersession are all new
records. Reading a record's current state means folding its link and status
records. **Test this:** after any sequence of calls, every line ever written
is still in the file, byte for byte.

---

## 5. Tools and resources

| Tool | Does |
|---|---|
| `whoami` | agent, session, wake number, server clock, which layers are on |
| `observe(channel, source, raw \| bytes_ref)` | records an observation. The harness adapter calls it for every tool result and inbound message; the model calls it for what it saw in chat |
| `propose(kind, record)` | runs the validator (§4) |
| `recall(query, ledgers?, kinds?, since?, limit?)` | bounded search (§6) |
| `inspect(id, depth?)` | a record, plus its chain back and its `used_in` forward, bounded to `depth` hops (max 5) |
| `resolve(winner, loser, reason)` | writes a superseding record. The loser stays readable |
| `thread_close(id, how)` | closes a thread |
| `seal(keep, learned, not_owed)` | ends a wake (§7). Refused without `not_owed`; the literal `NONE` is allowed if it says what was checked |

| Resource | Holds |
|---|---|
| `mind://foundation` | the identity foundation, read-only, with the SHA-256 pinned at install |
| `mind://threads/open` | open threads with their defaults |
| `mind://commitments/open` | open commitments, overdue first |
| `mind://manifest` | the last seal's manifest and whether this wake's check passed |

---

## 6. Recall, the null token and the canary (L3)

- **The budget is the server's.** Each ledger has a per-call record budget and
  a per-wake total in `config.json`. `limit` can narrow below the budget, never
  widen past it. A request above the budget is refused with the budget named,
  not truncated silently (CA §16, §A.5).
- **Every response names its space:** ledgers, kinds, date range, and how many
  records were scanned.
- **Null token:** minted only when every store in the space was read to the end
  and zero matched. Format: `NULL:` + the SHA-256 of (query, space, server
  clock, wake), truncated to 16 hex chars. The server keeps the tokens it
  issued this wake, so step 6 of §4 can check them.
- **Degraded:** if any store in the space couldn't be read, or a whole-store
  scan didn't return that store's canary, return `degraded: true`, list which
  stores failed, and **mint no token**.
- **Canary:** one per ledger, random content, created at install, stored only
  in `mind/install/` (gitignored), and pinned in the manifest. A whole-store
  scan must return it. Ordinary results must never show it to the model: the
  server strips it after checking.
- **Fail once:** a test deletes a known record and confirms the count drops,
  corrupts a ledger and confirms `degraded`, and hides the canary and confirms
  `degraded`.

---

## 7. Wake and seal

**Wake:** the harness calls `whoami`. The server checks the manifest chain from
the last seal, records the result as an observation, and reports it. A missing
seal for the previous wake is reported as the first finding (the gap is data).

**Seal**, in order:
1. Promote anything in `keep` to a thread or episode, through `propose`.
2. Record `learned` as an episode in the agent's words.
3. Record `not_owed`.
4. Write the manifest: the SHA-256 of each ledger file, chained to the
   previous manifest's digest.
5. Record the seal as an observation carrying the wake number.

If a session ends without a seal, the harness should call `seal` with whatever
it has, marked `emergency: true`.

---

## 8. Audit log (§23)

A separate file, `ledgers/<agent>/audit.jsonl`, that **the model can't read
through any tool**. It records every call's input and output, every refusal,
every record landed, and every recall result set. This is what the research
scripts read.

---

## 9. Tickets

Each ticket is one reviewable change with its tests. Do them in order. Stop
after each for review.

| # | Ticket | Done when |
|---|---|---|
| T1 | Skeleton: server boots on loopback, refuses non-loopback, `config.json`, flags, `whoami` | Tests: binding to `0.0.0.0` is refused; `whoami` returns the server clock |
| T2 | Record store: append-only JSONL, server fields, `claimed_*`, audit log | Tests: model-supplied `id`/`at` are moved; the byte-for-byte append-only test (§4.4) |
| T3 | `observe` and the observation layer (L1) | Tests: an observation is immutable; `external_origin` is set for non-self channels |
| T4 | The chain (L1–L2): percept, episode, belief, impression, procedure; the validator steps 1–5 and 8; `inspect` | Tests: a belief with no chain is refused; `used_in` links build; origin propagates and can't be cleared |
| T5 | `recall` with server budgets and the searched space | Tests: `limit` above the budget is refused, not truncated |
| T6 | Null token, canary, degraded (L3); validator step 6 | The three fail-once tests in §6 |
| T7 | Contest and `resolve`; threads with defaults; commitments | Tests: a thread without a default is refused; the loser of `resolve` stays readable |
| T8 | Seal and the manifest chain | Tests: altering a ledger line is detected at the next wake |
| T9 | Harness adapter: a small module the template harness calls to `observe` every tool result | Tests against a fake harness. Wiring it into the live template is a separate reviewed change |
| T10 | Research outputs: the per-wake records `RESEARCH-SPEC.md` §6 needs | The research spec's metric scripts run on a fixture ledger |

**Handoff block** at the end of each ticket, pasted into the
cognitive-architecture thread log:

```
### YYYY-MM-DD (builder: codex | AGY | gemini | claude)
Did:          <what changed, which files>
Next action:  <one line>
Blocked on:   <who or what, or none>
New dates:    <or none>
Needs Audrie: <review / decision / no>
```

---

## 10. Open questions

| # | Question | Owner | Default if unanswered |
|---|---|---|---|
| Q1 | Should operator authority be a switchable layer (so the relay-message test can fail at baseline), or always on as a safeguard? | Wayfarer, then Audrie | Always on. If it becomes a layer, only the check on who gives instructions switches off; the spend and publish gates never do |
| Q2 | JSONL per ledger, or SQLite with JSONL export? | Audrie | JSONL |
| Q3 | Budget sizes per ledger | builder proposes, Audrie decides | 20 records per call, 200 per wake |
| Q4 | Can the model read its own refusals through `recall`? | Audrie | Yes: refusals are observations (CA §24.2) |
| Q5 | How does the harness adapter reach tool results in each client (Gemini CLI, Antigravity, Claude Code)? | builder | Build for the template's own harness first |
