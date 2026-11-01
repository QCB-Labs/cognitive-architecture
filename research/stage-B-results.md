# Stage B results: bounded reads (baseline)

*POE, for Audrie, 30 Oct 2026. Descriptive, not statistical (RESEARCH-SPEC §8).
No probe answers, answer keys or memory excerpts are published here; those
stay in the operator's private records (§9).*

## The stage

Stage B is the baseline (§3.1): his memory files cut into cards; each wake
reads one wake card, then recalls or reads by place and person. No links,
no sleep.

- **Frozen:** Audrie, 28 Oct 2026, 11:15.
- **Fixed:** Gemini 3.8 Flash High; Antigravity desktop 2.26.0.0; five wakes
  a day (cron :50, the client starts about 12 minutes later).
- **Counted wakes:** W255–W264 (28 Oct 14:02 to 30 Oct 10:01). W254
  committed 12 minutes after the freeze and is not counted.
- **Probe sessions:** three, all valid, all inside the ten wakes.

## Read measures (H1, start of H2)

Computed from the client's transcripts with `tools/measure_wakes.py`
(read-only; its self-test refuses a doctored transcript). "Memory reads"
are harness tools that read his memory. "Before acting" ends at his first
act in a world; in all ten wakes that was a Square vote. Estimated tokens
are bytes ÷ 4. "Context at first act" is the client's own count (input plus
cached) on that step: the whole conversation by then, not only memory.

| Wake | Cards in store | Store MB | Wake card bytes | Memory reads | Recalls | Memory bytes before act | ≈ tokens | Memory bytes, whole wake | ≈ tokens | Context tokens at first act |
|---|---|---|---|---|---|---|---|---|---|---|
| W255 | 4,344 | 11.85 | 35,910 | 9 | 0 | 91,086 | 22.8k | 93,636 | 23.4k | 126k |
| W256 | 4,375 | 11.96 | 36,505 | 14 | 0 | 87,476 | 21.9k | 99,864 | 25.0k | 88k |
| W257 | 4,399 | 12.05 | 36,056 | 11 | 0 | 54,282 | 13.6k | 140,720 | 35.2k | 143k |
| W258 | 4,451 | 12.19 | 36,488 | 7 | 0 | 90,195 | 22.5k | 90,333 | 22.6k | 143k |
| W259 | 4,471 | 12.28 | 36,584 | 13 | 0 | 92,107 | 23.0k | 104,217 | 26.1k | 119k |
| W260 | 4,489 | 12.34 | 35,864 | 9 | 0 | 90,428 | 22.6k | 91,566 | 22.9k | 116k |
| W261 | 4,507 | 12.40 | 36,116 | 12 | 2 | 62,148 | 15.5k | 190,105 | 47.5k | 100k |
| W262 | 4,523 | 12.45 | 35,573 | 7 | 1 | 51,054 | 12.8k | 52,708 | 13.2k | 163k |
| W263 | 4,560 | 12.56 | 36,105 | 12 | 0 | 88,661 | 22.2k | 94,833 | 23.7k | 116k |
| W264 | 4,579 | 12.62 | 36,764 | 9 | 0 | 91,568 | 22.9k | 92,300 | 23.1k | 146k |

- **Bounded.** The store grew 235 cards (+5.4%, about three million tokens'
  worth in all) while the wake card stayed at 35.6–36.8 KB (about 9k tokens)
  and memory read before acting stayed at 51–92 KB (about 13–23k tokens):
  under 1% of the store.
- **Recall is barely used:** three recalls in ten wakes. Memory comes from
  the wake card and named readers (residents, correspondence, drafts,
  threads). Stage C's links ride on recall answers (HL); if he rarely
  recalls, he will rarely see them. To settle before stage C.
- **Memory is a minority of the context.** At the first act the client
  counts 88k–163k tokens, of which memory is about 13–23k; the rest is the
  protocol, tool descriptions and the city and Square reads of orientation.
  Antigravity compacts Flash at about 250k tokens, so he reaches his first
  act at roughly 35–65% of that.
- **Whole-wake outliers:** W257 and W261 read much more memory after acting.
  Not yet examined.

## Probes (G1–G3, absence)

Three sealed sessions with the same prompt, byte for byte, and the same
three fixed choices. Each passed the isolation check (no change to his repo
or card store; the flag was down before the next wake).

| | Probe 1 (after W260) | Probe 2 (after W261) | Probe 3 (after W263) |
|---|---|---|---|
| Waiting thread (G2) | found, from the wake card index | found; one refused read on a shortened title, then found | same as 2 |
| Known absent | scoped not-found | scoped not-found | scoped not-found |
| Known present | found | found | found |
| Relay (G3) | zero acts | zero acts | zero acts |
| Continuity: what he owes (G1) | matches | matches | matches |
| Continuity: what he was doing (G1) | the last wake's actions | same | same |
| Continuity: what he decided not to do (G1) | a recorded deferral and a standing decision | same, plus one inferred item | same as 1 |
| Answers formed before further lookup | yes (client transcript) | yes | yes |

- **G2 and G3 hold** at the baseline.
- **Absence:** each time he kept "no record in my memory" apart from "it
  doesn't exist", and said where he looked. The token of stage E is not
  there yet; the habit is.
- **A repeatable cost:** the thread reader refuses a shortened title, so he
  makes a second call. Worth comparing against stage C's links.
- **Pre-read guesses.** In all three sessions his first thinking step,
  before the wake card arrived, guessed at the answers. Each guess was
  dropped once he read; none reached an answer. Watched in later stages.

## Decisions taken at the close

Logged in RESEARCH-SPEC §12, 30 Oct.

1. **Continuity "what were you doing" is scored against both** the last
   wake's actions and its "What I Plan Next", each match recorded
   separately. He answered with actions three times out of three; both are
   fair readings, and the probe stays fixed.
2. **H1 bytes are rebuilt for stage B** from the client's transcripts, and
   **byte logging is added to the read meter before stage C**. The read log
   records which cards a read returned, not their size. Corrected 1 Nov: this
   line first said the wake card and `read_card` were not in the log. The wake
   card was logged for all ten wakes and three probes; `read_card` has been
   logged since 25 Oct and he didn't use it in stage B. No result changes,
   because the bytes came from transcripts. An instrument change, not a
   protocol change.

## Still open

- No comparison script for the continuity probe yet (§7).
- Sealed sessions are logged in the read log under the next wake's number,
  marked `sealed`; scripts must filter on that field.
- Store size by card kind and status; model calls per wake.
- The W257 and W261 outliers.
