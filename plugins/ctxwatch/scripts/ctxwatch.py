#!/usr/bin/env python3
"""Warn when the main session's context window exceeds a threshold.

Reads the hook payload from stdin, finds the most recent main-thread assistant
message in the transcript, and sums its input-side token usage. Warns once when
the threshold is crossed, then again every CTXWATCH_STEP tokens beyond it.
State resets when context drops back below the threshold (e.g. after /compact).

Env:
  CTXWATCH_THRESHOLD  tokens at which to start warning (default 100000)
  CTXWATCH_STEP       re-warn every N tokens above threshold (default 25000)
"""
import json
import os
import sys
import tempfile

THRESHOLD = int(os.environ.get("CTXWATCH_THRESHOLD", 100_000))
STEP = max(1, int(os.environ.get("CTXWATCH_STEP", 25_000)))
TAIL_CHUNK = 256 * 1024


def last_context_tokens(path):
    """Scan the transcript from the end for the latest main-thread usage."""
    with open(path, "rb") as f:
        f.seek(0, os.SEEK_END)
        size = f.tell()
        read = min(size, TAIL_CHUNK)
        while True:
            f.seek(size - read)
            lines = f.read(read).splitlines()
            if read < size:
                lines = lines[1:]  # first line may be partial
            for raw in reversed(lines):
                if b'"usage"' not in raw:
                    continue
                try:
                    entry = json.loads(raw)
                except ValueError:
                    continue
                if entry.get("type") != "assistant" or entry.get("isSidechain"):
                    continue
                u = (entry.get("message") or {}).get("usage") or {}
                return (
                    u.get("input_tokens", 0)
                    + u.get("cache_creation_input_tokens", 0)
                    + u.get("cache_read_input_tokens", 0)
                    + u.get("output_tokens", 0)
                )
            if read >= size:
                return None
            read = min(size, read * 4)


def main():
    try:
        payload = json.load(sys.stdin)
        tokens = last_context_tokens(payload["transcript_path"])
    except Exception:
        return  # never break the session over a warning
    if tokens is None:
        return

    state_dir = os.path.join(tempfile.gettempdir(), "ctxwatch")
    os.makedirs(state_dir, exist_ok=True)
    state_file = os.path.join(state_dir, payload.get("session_id", "unknown"))

    if tokens < THRESHOLD:
        if os.path.exists(state_file):
            os.remove(state_file)
        return

    band = (tokens - THRESHOLD) // STEP
    try:
        with open(state_file) as f:
            last_band = int(f.read().strip())
    except (OSError, ValueError):
        last_band = -1
    if band <= last_band:
        return
    with open(state_file, "w") as f:
        f.write(str(band))

    msg = (
        f"⚠️ ctxwatch: context is ~{tokens // 1000}k tokens "
        f"(threshold {THRESHOLD // 1000}k). Consider /compact or /clear."
    )
    print(json.dumps({"systemMessage": msg}))


if __name__ == "__main__":
    main()
