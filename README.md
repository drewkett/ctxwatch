# ctxwatch

A Claude Code plugin that warns you when the session's context window grows past a threshold (default **100k tokens**).

```
⚠️ ctxwatch: context is ~112k tokens (threshold 100k). Consider /compact or /clear.
```

## Install

```
/plugin marketplace add drewkett/ctxwatch
/plugin install ctxwatch@ctxwatch-local
```

## How it works

- Runs on `UserPromptSubmit` and `PostToolUse`, so it catches growth mid-turn too.
- Reads the latest main-thread assistant message's `usage` from the transcript (input + cache read + cache creation + output). Subagent messages are ignored.
- Warns once on crossing the threshold, then again every step (125k, 150k, …). Resets when context drops back below the threshold (e.g. after `/compact`).
- The warning is shown to you only; it isn't added to Claude's context. Failures exit silently.

## Configuration

| Env var | Default | Meaning |
| --- | --- | --- |
| `CTXWATCH_THRESHOLD` | `100000` | Tokens at which to start warning |
| `CTXWATCH_STEP` | `25000` | Re-warn every N tokens above the threshold |

Set them in your shell or under `env` in Claude Code settings. Requires `python3`.

## License

MIT
