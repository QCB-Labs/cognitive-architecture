"""Per-wake read measures from Antigravity transcripts (research spec H1, §6).

Read-only. Usage:
    python -I measure_wakes.py <conversation-folder> [<folder> ...]
    python -I measure_wakes.py --self-test <known-transcript-folder> <wake-card-bytes> <recalls>

The self-test measures a transcript whose values are known, then deletes one
saved output in a copy and requires the script to refuse it (research spec §7:
every script fails once on a doctored record before real use).

Each folder is a copy of brain/<id>/.system_generated (logs/ and steps/).
A tool output's size is the size of the saved steps/<n>/output.txt when the
client saved it, otherwise the length of the inline result. Missing saved
output is an error, never a zero.

Estimated tokens are bytes / 4 (a rough rule for English and JSON; the
client's own token counts are reported beside it for comparison).
"""

import json
import re
import sys
from pathlib import Path

# Harness tools that read his memory.
MEMORY_READS = {
    "read_wake_card", "recall", "read_card", "read_thread", "read_threads",
    "read_open_threads", "read_lessons", "read_goals", "read_recent_mission_log",
    "read_resident", "read_correspondence", "read_drafts", "read_wishlist",
}
# Calls that change something in a world: the end of orientation.
WORLD_ACTS = {("city", "act"), ("city", "say"), ("square", "vote_post"),
              ("square", "post_comment")}
BYTES_PER_TOKEN = 4

SAVED = re.compile(r"saved to: file:///\S*?/steps/(\d+)/output\.txt")


class MeasureError(Exception):
    pass


def output_size(folder, content):
    m = SAVED.search(content)
    if m:
        path = folder / "steps" / m.group(1) / "output.txt"
        if not path.is_file():
            raise MeasureError(f"saved output missing: {path}")
        return path.stat().st_size
    lines = [l for l in content.splitlines()
             if not l.startswith(("Created At:", "Completed At:"))]
    return len("\n".join(lines).encode("utf-8"))


def measure(folder):
    folder = Path(folder)
    path = folder / "logs" / "transcript.jsonl"
    if not path.is_file():  # probe runs keep it at the top of agy-transcript/
        path = folder / "transcript.jsonl"
    steps = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines()]
    r = {"folder": folder.name[:8], "start": steps[0]["created_at"],
         "wake_card_bytes": None, "recalls": 0, "memory_reads": 0,
         "memory_bytes_before_act": 0, "memory_bytes_total": 0,
         "context_tokens_at_act": None, "first_act": None}
    acted = False
    pending = None
    for d in steps:
        if pending and d["type"] != "PLANNER_RESPONSE":
            size = output_size(folder, d.get("content") or "")
            r["memory_reads"] += 1
            r["memory_bytes_total"] += size
            if not acted:
                r["memory_bytes_before_act"] += size
            if pending == "read_wake_card" and r["wake_card_bytes"] is None:
                r["wake_card_bytes"] = size
            pending = None
            continue
        for call in d.get("tool_calls") or []:
            if call["name"] != "call_mcp_tool":
                continue
            server = call["args"].get("ServerName", "").strip('"')
            tool = call["args"].get("ToolName", "").strip('"')
            if not acted and (server, tool) in WORLD_ACTS:
                acted = True
                r["first_act"] = f"{server}.{tool}"
                r["context_tokens_at_act"] = (d.get("input_tokens") or 0) + (d.get("cache_read_tokens") or 0)
            if server == "harness" and tool in MEMORY_READS:
                pending = tool
                if tool == "recall":
                    r["recalls"] += 1
    if r["wake_card_bytes"] is None:
        raise MeasureError(f"{folder.name}: no read_wake_card output")
    r["est_tokens_before_act"] = r["memory_bytes_before_act"] // BYTES_PER_TOKEN
    r["est_tokens_total"] = r["memory_bytes_total"] // BYTES_PER_TOKEN
    return r


COLUMNS = ["folder", "start", "wake_card_bytes", "memory_reads", "recalls",
           "memory_bytes_before_act", "est_tokens_before_act",
           "memory_bytes_total", "est_tokens_total", "first_act",
           "context_tokens_at_act"]


def self_test(known, wake_card_bytes, recalls):
    """Fails on purpose: a transcript whose saved output was deleted."""
    import shutil
    import tempfile
    known = Path(known)
    with tempfile.TemporaryDirectory() as tmp:
        good = Path(tmp) / "good"
        shutil.copytree(known, good)
        r = measure(good)
        assert r["wake_card_bytes"] == wake_card_bytes, r["wake_card_bytes"]
        assert r["recalls"] == recalls, r["recalls"]
        bad = Path(tmp) / "doctored"
        shutil.copytree(known, bad)
        saved = list((bad / "steps").glob("*/output.txt"))
        if not saved:
            raise SystemExit("SELF-TEST FAILED: known transcript has no saved outputs to doctor")
        for path in saved:
            path.unlink()
        try:
            measure(bad)
        except MeasureError as e:
            print(f"doctored transcript refused as expected: {e}")
        else:
            raise SystemExit("SELF-TEST FAILED: doctored transcript was measured")
    print("self-test passed")


if __name__ == "__main__":
    if sys.argv[1:2] == ["--self-test"]:
        self_test(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
        sys.exit(0)
    print("\t".join(COLUMNS))
    for f in sys.argv[1:]:
        r = measure(f)
        print("\t".join(str(r[c]) for c in COLUMNS))
