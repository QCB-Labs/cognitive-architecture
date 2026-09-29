# Research methods: working with LLM assistance

*How research in this repo is run. Written by POE, for Audrie, 2026-09-29.
Applies to the research spec, idea files and any paper that comes out of
them. Pairs with CA §30.2: cite only after reading.*

**Scope.** This covers LLMs used as research assistants. LLMs as the
subjects of the study are governed by `RESEARCH-SPEC.md`.

**Principle.** LLMs are used as **tools for finding and handling material**,
never as **sources of evidence**. Every claim in our work traces to a primary
source that a human has read.

---

## 1. What an LLM may do

- Suggest search terms and candidate sources (a literature *map*).
- Fetch, list and check metadata: do the IDs exist, do titles and dates match.
- Help a human read a paper: locate sections, explain methods, point to
  tables. The human confirms each point against the page.
- Draft wording from notes the human wrote, which the human then revises.
- Check our text against our notes for errors and overclaims.

## 2. What an LLM may not do

- Be cited, or supply any claim, number or quote that appears in our work.
- Stand in for reading: a model's summary is never the basis of a citation.
- Supply a "nobody has done X" claim. Gap claims need our own recorded
  search.
- Score or judge results in our study outside the model-lineage rules in
  `RESEARCH-SPEC.md` (R2).

## 3. Literature search

1. **Seed.** An LLM search may propose candidates. Its output is saved
   unedited, dated, with the prompt used and the exact model, version and
   setting that produced it (e.g. "GPT-5.6 Sol, medium, via Codex").
2. **Own search.** We run our own searches on Google Scholar, arXiv and
   Semantic Scholar, and record each database, search terms, date and hit
   count in a search log.
3. **Screen.** Titles and abstracts first. Each source is recorded as
   included or excluded, with a one-line reason.
4. **Snowball.** Check the references of included papers and the papers that
   cite them. Log those too.
5. **Gap claims** ("not found") are stated with the search log behind them,
   and a date.

## 4. Reading and extraction

- For each source we rely on, a **reading note** in our own words: the
  question, method, sample, main result with its number and page or table,
  stated limits, and our assessment.
- **Number rule.** Every figure we use is copied from the paper's own table
  or text and noted with its page. Never from a summary.
- **Read tiers.** *Full* for sources the argument depends on. *Abstract and
  relevant section* for supporting ones. *Secondary* for classics cited
  through a review we read, and we say so: "(X 1997, as reviewed in
  Y 2011)".
- **[unreviewed]** marks any claim or number that came from a search or a
  summary rather than from reading the source. It stays until the claim has
  been checked against the paper, then comes off. Unreviewed claims may sit
  in working files, always with a link to the source; they never reach a
  finished paper.
- **Evidence label** on each claim: *established*, *reported* (a single
  study or a preprint) or *speculative* (our inference).

## 5. Writing

- Citations point only at sources with a reading note.
- Our own sentences, never a lightly edited LLM paraphrase.
- Preprints are marked as preprints. Recent ones are rechecked for new
  versions before a final draft.

## 6. Disclosure

**On each drafted document.** Any document an LLM drafted ends with a line
naming the model, the date, whose ideas it records, and whether the human
has reviewed it:

> *Drafted by <model> (<desk or tool>) from conversation with <person>,
> <date>. Ideas and direction: <person>. Reviewed by <person>: pending.*

When reviewed, "pending" becomes the review date. Documents written by a
human carry no line.

**For any public paper:**

> An AI-assisted literature search was used to identify candidate sources.
> All cited claims were verified against the original publications by the
> authors. AI tools assisted with drafting; the authors reviewed all text.

## 7. Records

Kept privately, outside this repo, in the project vault
(`02 future-builds/Cognitive Architecture/Research/`), with templates for the
search log and reading notes:

- Raw LLM search outputs and the prompts that produced them, unedited and
  dated.
- The search log.
- Reading notes.
- The decision log: sources included or excluded, and claims changed after
  reading, with reasons.

Public here: this file, the specs, idea files, and the finished citations.

---

*Drafted by Claude Opus 5.5 (POE desk, Claude Code) from conversation with
Audrie, 2026-09-29. Ideas and direction: Audrie. Reviewed by Audrie: pending.*
