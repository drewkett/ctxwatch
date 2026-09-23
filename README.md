# ctxwatch

A Claude Code plugin that tells Claude when the session's context window grows past a threshold (default **100k tokens**), so it can work leaner and suggest `/compact` or `/clear` at a natural stopping point. You also see a one-line notice:

```
⚠️ ctxwatch: context is ~112k tokens (threshold 100k).
```

## Install

```
/plugin marketplace add drewkett/ctxwatch
/plugin install ctxwatch@ctxwatch
```

## How it works

- Runs on `UserPromptSubmit` and `PostToolUse`, so it catches growth mid-turn too.
- Reads the latest main-thread assistant message's `usage` from the transcript (input + cache read + cache creation + output). Subagent messages are ignored.
- Warns once on crossing the threshold, then again every step (125k, 150k, …). Resets when context drops back below the threshold (e.g. after `/compact`).
- The warning goes to Claude via `additionalContext` (about 60 tokens per warning), telling it to keep context lean and suggest `/compact` or `/clear` at the next stopping point, not mid-task. It's also shown to you via `systemMessage`.
- Failures exit silently.

## Configuration

| Env var | Default | Meaning |
| --- | --- | --- |
| `CTXWATCH_THRESHOLD` | `100000` | Tokens at which to start warning |
| `CTXWATCH_STEP` | `25000` | Re-warn every N tokens above the threshold |

Set them in your shell or under `env` in Claude Code settings. Requires `python3`.

## License

MIT
