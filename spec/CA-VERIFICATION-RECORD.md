# Verification record

Housekeeping for the Cognitive Architecture Specification. Kept separate so the specification stays clean.

**Sources checked**

| Source | Commit | Reachable |
|---|---|---|
| `qualitycontrolbureau/Sputnik` | `b829f8a` | yes |
| `qualitycontrolbureau/agent-harness-template` | `2267378` | yes |
| `waypostmaster/waypost` | `ab49815` | yes |
| `EmergenceAI/Emergence-World` | `57d0d38` | yes |
| Emergence World Season 2 paper | — | **no — blocked by network policy. Not read.** |

---

## 1. Supporting document withdrawn

*Architectural Synthesis: Waypost (#273) & The Cognitive Architecture* is **withdrawn**. Do not cite it until it is rewritten.

### What holds

Three files it names exist: `Symmetric_Trust_Layer_Specification.md` (1053 lines), `LODESTONE.md` (138 lines), `skills/subagents-mistaken-for-humans_v1.0.md` (114 lines).

### What does not

| Cited | Actual |
|---|---|
| STL §6.5a–c, *Compression Debt & The State Bounding Invariant* | §6.5a *Every deferral carries a named deadline*; §6.5b *The Collision Register*; §6.5c *The deferral reckoning* |
| STL §6.5b, *Echo-Graph Attenuation* | §6.5b is the Collision Register |
| STL §1.7, *The Read-Only Constant Defect* | §1.7 exists as *Used constants audit themselves. Read-only constants do not.* Adjacent title, different subject |
| STL Part 8, *Caller Authentication Invariance* | Part 8 is *The record: manifests, git, anchors* |
| STL Part 11b, *The Gate Invariant* | Part 11b is *What the files cannot carry* |
| STL §4.2, *Asymmetric Authority Gradient* | §4.2 is *Ground every claim in the corpus* |
| LODESTONE §3.4 *Core Drift Detection*, §3.7 *Mechanical Arrest*, *Pruning Dynamics* | LODESTONE.md has no numbered sections. Nine prose headings, none of these |
| `origin_root_id`, `transmission_depth`, echo-graph attenuation, γ = 0.85, Growth Ratio ≤ τ = 0.25, `contested_halt`, Keyed Root Dereferencing | Zero occurrences anywhere in the repository |
| Sputnik has 42 tools | 56 |
| `harness_mcp.py` contains `gate_invent_kind` | Wrong name, right mechanism — see below |

**"Compression debt" is real and is not a protocol.** It appears five times in the trust-layer specification as the author's running self-accounting that the document keeps promising to contract and keeps growing: 115.2%, 111.2%, 106.1%, 117.5%, settling at 113.8%. It is a note about document length. There is no contraction ratio, no debt ledger, no admission threshold, nothing that gates memory.

### The gate: wrong name, right mechanism

`harness.invent_kind` existed. Journal entry W050 proposed renaming it `gate_invent_kind` for clarity against the world API's own `invent_kind`. That rename never happened. What shipped instead was `authorise_spend`, generalised from one paid act to all six.

The synthesis document also states that the harness trips the spending permission bit. It does not. `authorise_spend` reads that switch and never writes it; the operator sets it. **The implementation is stricter than the document claimed.**

### Two failures, weighted differently

**Citation drift** (the Sputnik claims). A real mechanism described roughly right, labelled with a name that was proposed and never adopted, with a stale count. Someone reading it builds the right thing and calls it the wrong name.

**Fabrication** (the Waypost claims). Section numbers, titles, constants and field names for mechanisms not in the repository under any name. Someone reading it builds something nobody has built and believes it was field-tested.

What they share is the surface. Both are confident, internally consistent, and precisely cited. **Precision of citation is not evidence of accuracy.** In both cases it is what made the claim persuasive.

### Rule adopted

> A citation to a section number in an external document is *carried* until that section has been read at a named commit.

No supporting document enters the set carrying an unverified section number, constant, or named mechanism. This is §30.3 of the specification.

---

## 2. What survived the withdrawal

Three ideas from the withdrawn document are sound independently of its citations and are carried into the specification without attribution to it:

- **Counting evidence over unique origins** rather than over the number of people repeating it → §33, answered-in-principle
- **Bounded consolidation** → §14.5
- **`subagent_report` as a provenance type with zero instructional authority** → §8.1, now grounded in a primary source (`subagents-mistaken-for-humans_v1.0.md`) rather than a claim about one

Counting correlated evidence by unique source is standard. It did not need the citation to be true.

---

## 3. Corrections made to the specification during this pass

| Claim | Corrected to |
|---|---|
| "sixty wakes" (6 occurrences) | eighty-three — `budget.json` `wake_count: 83`, latest journal entry W083 |
| Order of authority has six ranked sources | five |
| Template ships 55 of the reference implementation's 56 tools | 55 and 56; not a subset — the sets differ |
| Lessons file is 263 lines | that is the reference implementation's file, not the template's |
| No `propose_` verb anywhere in the interface | `propose_city_rule` exists |
| `correspondence/`, `acquired/`, `private/`, `replay/`, `drafts/` listed as tree contents | gitignored; real at runtime, absent from version control |

**One false alarm, checked and dismissed.** Thirty-three tool names appear in the template's documentation with no matching function definition. This is not a defect. `naming.json` maps canonical internal keys to a swappable presentation scheme, with three schemes shipped and exactly 33 mappings. This became §27.2 of the specification.

---

## 4. Outstanding

**Emergence World Season 2 paper.** Not read — the publisher's domain and the preprint server are both blocked by this environment's network policy. Everything in §30.1 comes from the project's public repository or is marked as unread. Any claim depending on Season 2 results needs checking against the paper.

**Licence terms to observe.**

- Emergence World: CC BY-NC 4.0, research use only, attribution required. Their datasets may not be used to train, evaluate or benchmark models for commercial purposes.
- Waypost trust-layer specification: CC BY 4.0, inside a repository otherwise AGPL-3.0. Adapt with attribution. Its own upstream sources are not all reusable — cite that document, not through it.
