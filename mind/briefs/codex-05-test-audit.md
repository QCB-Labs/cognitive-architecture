# Codex brief 05: are Sputnik's tests any good? (audit, no fixes)

*Paste this whole file into Codex. Written by POE for Audrie, 2026-09-30
(v2: measured staleness + a mutation tool, hand breaks as fallback).
Work repo: **`dev\sputnik`**, new branch **`audit/test-usefulness`**.
Busy work for spare quota. Nothing here changes Sputnik.*

---

Hi Codex. Sputnik's repo has about 570 tests on `main`. They all pass.
Passing proves little: a test that can't fail protects nothing. Find out
**which tests are stale or weak, and which code no test would protect if it
broke.** Measure first; read closely only what the numbers flag. This is an
audit: you **report**, you don't fix. Follow the steps in order; if a step
can't be done as written, stop and report.

## Paths

`%USERPROFILE%` is the Windows user folder; resolve it first.

| Name | Full path | Access |
|---|---|---|
| WORK | `%USERPROFILE%\dev\sputnik` | read; write only temporary code breaks on the audit branch |
| OUT | `%USERPROFILE%\dev\scratch-audit05` | write: the audit venv, logs, tool output, the report |

Pytest's own default temp folder is allowed. Never touch the vault copy of
Sputnik (`%USERPROFILE%\Documents\World Sim\08 Agent testing\sputnik`).

## Rules

- **Do not commit and do not push.** Ever, in this brief.
- **Install tools only into `OUT\venv`**, never into the system Python or
  anything inside WORK. Audrie has approved installing: the packages in
  WORK's `requirements-mcp.txt`, `pytest-cov`, and one mutation-testing tool
  (Step 4).
- **Don't change any test and don't fix anything.** Report it.
- **Every code break is undone.** WORK's `git status` must be clean at the
  end of each step and at the end of the brief.
- Don't touch `memory\`, `GEMINI.md`, `GOVERNANCE.md`, `soul.md`, `goals.md`.
- **No real network calls** to the city, market, Square or email. If a test
  tries to reach the network, note it and move on.
- Keep a running log in `OUT\audit-log.md`, so a stop halfway still leaves
  a usable record.

## Step 1. Branch, venv, baseline

In WORK:

```
git status
git switch main
git log --oneline -1
git switch -c audit/test-usefulness
```

`git status` must be clean. Then create the venv **in OUT**:

```
python -m venv "%USERPROFILE%\dev\scratch-audit05\venv"
"%USERPROFILE%\dev\scratch-audit05\venv\Scripts\python" -m pip install -r requirements-mcp.txt pytest-cov
```

From now on, use that venv's `python` for everything. Run the suite:
`python -m pytest -q`. Record the commit and pass/fail/skip counts. If
anything fails on a clean `main`, stop and report.

Save per-file test counts: `python -m pytest --collect-only -q`.

## Step 2. Measure: what each test actually runs (staleness)

Run the suite with per-test coverage of `tools\`:

```
python -m pytest -q --cov=tools --cov-context=test --cov-report=
python -m coverage json --show-contexts -o "%USERPROFILE%\dev\scratch-audit05\coverage.json"
```

(Write coverage data files to OUT, not WORK, if the tool allows; otherwise
delete them from WORK afterwards and confirm `git status` is clean.)

From the data, report:
1. **Code no test runs:** per `tools\` file, the uncovered lines, and whole
   functions with zero coverage. Mark which are in the safety areas (Step 4).
2. **Tests that run no `tools\` code at all** (they check something else:
   docs, text, fixtures). List each one and what it checks instead.
3. **Tests that add nothing unique:** every line they cover is also covered
   by another test. List them. (Not necessarily bad, but candidates.)
4. **Skipped and expected-fail tests,** with their reasons.

## Step 3. Read only what Step 2 flagged

For the tests in 2.2, 2.3 and 2.4, read each and classify:
- **Asserts its own string:** checks text it wrote itself, not behaviour.
- **Can't fail:** no real assertion, or catches every exception.
- **Tests the mock:** everything real is faked.
- **Duplicate:** same check, same way, as another test.
- **Checks presence, not behaviour** (e.g. "a word appears in GEMINI.md").
  Say whether it's still worth keeping. Sometimes it is, for rules that must
  stay in the protocol.
- **Stale:** tests something that no longer exists or no longer matters.
- **Fine:** looked suspicious but earns its place. Say why.

## Step 4. Mutation testing on the safety code

A mutation tool makes many small breaks automatically and runs the tests
against each. Target these areas, in order:

1. **Spending:** the spend gate, `authorise_spend`, `pay_armed` checks.
2. **Authority:** who counts as the operator; email is conversation, never
   orders; signed-command checks.
3. **Privacy and release:** `tools\release.py`, the outgoing check,
   anything that stops private data leaving.
4. **Identity:** the soul foundation block that can't be overwritten.
5. **Memory writes:** mission log numbering, safe file replace.

First find which `tools\` files hold each area, and list them in the log.

**Tool:** try `cosmic-ray` first (it supports Windows); install it into the
OUT venv. If it can't be made to work within about 20 minutes, try
`mutmut`. Keep all tool config, databases and output in OUT. If the tool
needs a config file inside WORK, create it, and delete it at the end.

Run the tool on the files from areas 1–4 first, then 5. Use the fast test
subset for each file if the tool supports it; otherwise the whole suite.
It's fine if this runs a long time: it uses computer time, not your
quota. If it's going to take more than about three hours, run areas 1–4
only and say so.

Record: mutants made, killed (a test failed), survived (all tests passed),
and timed out or errored, per file.

**Fallback, only if neither tool works:** break the code by hand, one
change at a time (flip a condition, remove a check, move a limit by one,
fake a "success", swap arguments). Run the tests, record what failed,
restore with `git checkout -- <file>`, confirm clean. At least 40 breaks,
at least 5 in each of areas 1–4.

## Step 5. Look at every surviving mutant in areas 1–4

For each survivor in spending, authority, privacy or identity code: show
the change, say whether it's a **real gap** (a bug of that shape would
slip through) or **harmless** (for example it only changes a log message,
or it's equivalent code). Real gaps are the most important output.

## Step 6. Report

Write `OUT\test-audit-report.md` and paste this summary into the chat:

```
## Report: Codex brief 05 (test usefulness audit)

Model: <exact model and setting>
Branch: audit/test-usefulness (from <commit>)
Committed anything: no
WORK clean at the end: yes / no
Installed (OUT venv only): <packages and versions>

Baseline: <passed> passed, <failed> failed, <skipped> skipped

### Staleness (measured)
tools/ lines not run by any test: <n> of <n> (<%>)
Functions with zero coverage in safety areas: <list>
Tests that run no tools/ code: <n>   Tests adding nothing unique: <n>
Skipped / xfail: <n>, reasons: <short>

### Flagged tests, read (Step 3)
Asserts own string: <n>   Can't fail: <n>   Tests the mock: <n>
Duplicate: <n>   Presence-only: <n> (keep <n>)   Stale: <n>   Fine: <n>
<each non-fine one: test name, kind, one-line reason>

### Mutation testing
Tool: <cosmic-ray / mutmut / hand breaks>, run time: <h:mm>
Area:            made / killed / survived / other
  Spending:        <n> / <n> / <n> / <n>
  Authority:       <n> / <n> / <n> / <n>
  Privacy/release: <n> / <n> / <n> / <n>
  Identity:        <n> / <n> / <n> / <n>
  Memory writes:   <n> / <n> / <n> / <n>

### Real gaps (the important part)
<each surviving mutant judged a real gap: file:line, the change, why no
test noticed, what a test would need to check>

### Top 5 recommendations, most important first
1. ...

### Handoff
Did:          <one line>
Next action:  <one line>
Blocked on:   <or none>
New dates:    none
Needs Audrie: <review / decision / no>
```

**Stop after the report.** Don't write tests or fix anything; that becomes
its own brief once Audrie and POE have read this. Leave OUT in place for
review.
