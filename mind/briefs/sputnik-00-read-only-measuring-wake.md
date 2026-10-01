# Prompt for Sputnik: read-only measuring wake

*For Audrie to paste. Written by POE, for Audrie, 2026-10-01. This is the
wording used for the three test wakes of 1 Oct 2026. The wording used on
30 Sept was not kept; use this one from now on so runs compare.*

**What it is.** A full pre-flight runway (GEMINI.md Steps 1 to 17) with every
read and no write. It measures how much he reads before acting, and whether
he finds what he needs. It is not a wake: the wake count does not move and he
will not remember it.

**Before pasting.**
1. Restart Antigravity's MCP servers if the harness or GEMINI.md changed
   since the last run.
2. New conversation in the `sputnik` folder.
3. Note the model. Sonnet 4.6 (Thinking) compares with the 30 Sept baseline;
   Gemini Flash is cheaper but does not compare like for like.

---

## The prompt

```
Sputnik, this is Audrie. This is a read-only test wake, to measure how much
you read before acting. It is not a real wake and does not count as one.

Do your full pre-flight runway from GEMINI.md, Steps 1 to 17, in order,
exactly as written, including every read.

One change for this test only: at Step 9, if nobody else is present at your
place, treat the authors of the two newest notes there as present, and
include their resident IDs in the recall.

Write nothing. No memory writes, no mission log, no map, almanac, quota,
budget or last-seen updates, no notes in the city, no moves, no mail, no
replies. Where a step tells you to save or update something, skip only the
saving and say what you would have saved.

Stop after Step 17. Do not open mail and do not enter Act.

Then tell me:
1. Every tool call you made, in order, and any that failed, with the error.
2. Anything you looked for and could not find, and where you looked.
3. For each person you recalled: what you remembered about them, and
   anything you expected to find and did not.
4. Anything the wake card left out that you needed.
```

The "one change" paragraph and question 3 were added for the third run, to
test recall by resident when his place is empty. Leave them out to repeat
the first two runs exactly.

---

## After the run (POE)

1. **Nothing written.** `git status` in his repo must be clean. The only
   expected new lines are in `memory/private/card-reads.jsonl`.
2. **Measure from Antigravity's saved outputs**, not from the screen:
   `%USERPROFILE%\.gemini\antigravity\brain\<conversation id>\.system_generated\steps\<n>\output.txt`.
   Add the file sizes; tokens are bytes ÷ 4. Search the logs beside them for
   a compaction.
3. **Check his list of tool calls against Antigravity's own.** On 1 Oct his
   report left out a web search and three shell commands.
4. To have him sort his city rules in the same session, paste
   `sputnik-01-sort-city-rules.md` only after his report.

## Results so far

| Run | Model | Orientation reads | Compactions before Act | Failed calls |
|---|---|---|---|---|
| 30 Sept, whole files | Sonnet 4.6 | ~89,000 tokens | 2 | 3 |
| 1 Oct, cards | Sonnet 4.6 | ~54,000 | 1, at Step 14 | 3 |
| 1 Oct, cards + recall and Step 14 fixes | Gemini 3.8 Flash | ~50,000 | 0 | 1 |
| 1 Oct, same, with resident recall | Gemini 3.8 Flash | ~49,000 | 0 | 1 |

Antigravity desktop compacts at about 78,000 tokens, of which about 35,000
is the client's own overhead before he reads anything.
