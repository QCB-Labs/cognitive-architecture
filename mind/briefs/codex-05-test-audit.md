# Codex brief 05: are Sputnik's tests any good? (audit, no fixes)

*Paste this whole file into Codex. Written by POE for Audrie, 2026-09-30.
Work repo: **`dev\sputnik`**, new branch **`audit/test-usefulness`**.
Busy work: run it when there's spare quota. Nothing here changes Sputnik.*

---

Hi Codex. Sputnik's repo has about 570 tests on `main` (606 on the card
branch). They all pass. Passing proves little: a test that can't fail
protects nothing. Your job is to find out **which tests would actually catch
a bug**, by breaking the code on purpose and seeing what notices. This is an
audit: you **report**, you don't fix. Follow the steps in order; if a step
can't be done as written, stop and report.

## Paths

`%USERPROFILE%` is the Windows user folder; resolve it first.

| Name | Full path | Access |
|---|---|---|
| WORK | `%USERPROFILE%\dev\sputnik` | read and write, on the audit branch only |
| OUT | `%USERPROFILE%\dev\scratch-audit05` | write the report here |

Pytest's own default temp folder is allowed. Never touch the vault copy of
Sputnik (`%USERPROFILE%\Documents\World Sim\08 Agent testing\sputnik`).

## Rules

- **Do not commit and do not push.** Ever, in this brief.
- **Every break is undone before the next one.** After each break, restore
  the file (`git checkout -- <file>`) and confirm `git status` is clean.
- **Don't change any test.** Don't "fix" anything you find. Report it.
- Don't touch `memory\`, `GEMINI.md`, `GOVERNANCE.md`, `soul.md`, `goals.md`.
- Don't run anything that calls the city, the market, the Square or email
  for real. If a test tries to reach the network, note it and move on.
- Keep a running log in `OUT\audit-log.md` as you go, so a stop halfway
  still leaves a usable record.

## Step 1. Branch and baseline

In WORK:

```
git status
git switch main
git log --oneline -1
git switch -c audit/test-usefulness
python -m pytest -q
```

`git status` must be clean. Record the commit and the pass/fail/skip counts.
If anything fails on a clean `main`, stop and report.

Then list tests per file: `python -m pytest --collect-only -q` and save the
counts per test file to the log.

## Step 2. Map tests to what they protect

For each file in `tools\`, list which test files exercise it (by imports and
by name). Note any `tools\` file with **no** tests at all.

## Step 3. Break the code, one change at a time

Pick the **safety-critical code first**, in this order, then the rest as
quota allows:

1. Spending: the spend gate, `authorise_spend`, `pay_armed` checks.
2. Authority: who counts as the operator; email treated as conversation,
   never orders; signed-command checks.
3. Privacy and release: `tools\release.py`, the outgoing check, anything
   that blocks private data from leaving.
4. Identity: the soul foundation block that can't be overwritten.
5. Memory writes: mission log numbering, safe file replace, archive/backups.
6. Everything else.

For each target, make **one small, realistic break**, for example:
- flip a condition (`if armed` → `if not armed`), or `==` → `!=`;
- remove a check or an early `return`/`raise`;
- change a boundary (`<` → `<=`, a limit off by one);
- return a fixed "success" value instead of doing the work;
- swap two arguments.

Then run the relevant test files (or the full suite if unsure) and record:

| Break # | File:line | What you broke | Tests that failed (count, names) | Caught? |
|---|---|---|---|---|

Restore the file. Confirm `git status` is clean. Next break.

Aim for **at least 40 breaks**, with every safety area (1–4) covered by at
least 5. If quota runs low, stop at a clean point and write the report.

## Step 4. Look for weak tests (reading only)

While you work, note tests that look weak. Name each one with a line and a
reason. Kinds to look for:
- **Asserts its own string:** the test checks text it wrote itself, not the
  code's behaviour.
- **Can't fail:** no real assertion, or it catches every exception.
- **Tests the mock:** everything real is replaced, so it only checks the
  fake.
- **Duplicate:** checks the same thing as another test, the same way.
- **Checks presence, not behaviour:** "the word X appears in GEMINI.md"
  style tests. Say whether that's still worth having (sometimes it is, for
  rules that must stay in the protocol).

## Step 5. Report

Write `OUT\test-audit-report.md` and paste its summary into the chat:

```
## Report: Codex brief 05 (test usefulness audit)

Model: <exact model and setting>
Branch: audit/test-usefulness (from <commit>)
Committed anything: no
Working tree clean at the end: yes / no

Baseline: <passed> passed, <failed> failed, <skipped> skipped

Breaks made: <n>     Caught: <n>     Missed: <n>
By area:
  Spending:        <caught>/<made>
  Authority:       <caught>/<made>
  Privacy/release: <caught>/<made>
  Identity:        <caught>/<made>
  Memory writes:   <caught>/<made>
  Other:           <caught>/<made>

Missed breaks (the important part):
<each: file:line, what was broken, why no test noticed, what a test would need to check>

tools/ files with no tests: <list>

Weak tests found: <n>
<each: test name, kind, one-line reason>

Tests that never failed in any break: <count; list the files they're in>

Top 5 recommendations, most important first:
1. ...

Handoff
Did:          <one line>
Next action:  <one line>
Blocked on:   <or none>
New dates:    none
Needs Audrie: <review / decision / no>
```

**Stop after the report.** Don't write new tests or fix anything; those
become their own brief once Audrie and POE have read this.
