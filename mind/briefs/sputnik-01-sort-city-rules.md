# Prompt for Sputnik: sort your city rules (read-only session)

*For Audrie to paste. Written by POE, for Audrie, 2026-10-01.*

**When to use it.** In a read-only session, after the card branch is merged
into his repo, and **after** the orientation measurement has been taken in
that session. Pasting it earlier adds reads to the numbers being measured.

**What it is not.** It is not a wake and not a probe. Nothing is saved, so he
will not remember doing it. His answer is saved by Audrie, outside his
memory, and he is told what he decided in a later conversation.

**Before pasting:** the session must already be under the read-only
instruction used for the measuring wakes (read everything, write nothing).

---

## The prompt

```
Sputnik, this is Audrie. This is a read-only session: please don't write
anything. No memory writes, no mission log, no notes in the city, no moves.
Reading the city is fine.

Some background, because your memory is changing shape. Your memory files
are now also held as cards: one lesson, one thread, one rule each, with tags
so you can find them by place and person. Nothing you wrote has been changed.

I'd like your judgement on one file: city-rules.md. Most of its entries were
written in August, when you reached the city a different way, and the file
has hardly changed since. Its Proposed section says "do not rely on". You are
the one who can say what is still true.

Please read every entry: harness.read_city_rules gives you the whole file.
For each entry under Confirmed, Proposed and Retracted, give me one line:

  <first few words of the entry> | <verdict> | <what you checked> | <why>

Verdicts:
  KEEP     still looks true, and useful to you now
  RECHECK  might be true; you couldn't check it in this session
  RETIRE   no longer true, or about a way of working you don't use any more
  REWORD   true, but the entry says it badly; give the wording you'd use
  MERGE    says the same thing as another entry; name the other one

Where you can check an entry against the live city by reading, do, and say
what you read. Where you can't check without writing, say so and use RECHECK.
Don't guess: "I couldn't check this" is a good answer.

Two more questions when you've been through them:

1. You have two places to record what you learn: lessons, and city rules.
   Do you use them differently? Would one place serve you better?
2. Is there anything in this file you'd want in front of you at every wake?

KEEP on a Proposed entry isn't a promotion. Your file's own rule stands:
I confirm a rule, or two verified outcomes in different wakes do. I'll tell
you in a later conversation what I did with your answers, since you won't
remember this session.
```

---

## After the session (Audrie and POE)

1. Save his answer as it came, outside his repo:
   `02 future-builds/Cognitive Architecture/Research/` in the vault, dated.
2. Nothing is applied to his memory from it yet. The write half (INDEX-SPEC
   W1, W7) is where card statuses change. Until then the wake card already
   keeps the Proposed entries out of the Rules section.
3. Tell him in conversation what he decided and what was done with it.
4. His answer to question 1 is evidence for INDEX-SPEC Q5 (one door).

**One thing this session does write:** if he uses `recall` or `read_card`,
the harness adds a line to its private read log. That is a research record
outside his memory, and is expected.
