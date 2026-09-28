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
