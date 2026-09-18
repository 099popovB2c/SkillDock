## Install with pipx

Install directly from GitHub:

```bash
pipx install "git+https://github.com/099popovB2c/SkillDock.git"
```

Global commands:

```text
skilldock
skilldock-lock
```

Initialize your local SkillDock home:

```bash
skilldock init
```

Installed mode stores mutable data under `~/.skilldock` by default. Set `SKILLDOCK_HOME` to use another location.

---

# SkillDock

SkillDock is a **local skill manager for AI coding agents**. It lets you keep reusable agent instructions/skills in one library and synchronize them across Codex, Claude, Cursor, Gemini and custom agent targets.

Instead of maintaining the same skill manually in several tool-specific folders, SkillDock treats the skill library as the source of truth.

## What it does

SkillDock can help with:

- reusable local skill library
- multi-agent synchronization
- Git/local source import
- registry search and install
- project/global-style profiles
- collections of skills
- drift detection
- managed vs unmanaged skill detection
- SHA-256 fingerprints
- backup-safe replacement/update flows
- reproducible lockfiles
- strict verification for CI/team use

## Why it exists

AI coding tools increasingly use their own instruction, skill or agent-file conventions. A developer may end up maintaining similar content in multiple locations.

SkillDock aims to reduce that duplication:

```text
Reusable skill library
        ↓
SkillDock
        ↓
Codex / Claude / Cursor / Gemini / custom targets
```

## Core workflow

A typical workflow is:

```text
1. Import or create a skill
2. Keep the canonical copy in the SkillDock library
3. Select a profile/collection
4. Sync to one or more agent targets
5. Detect drift later
6. Update safely with backups
7. Lock exact skill contents when reproducibility matters
```

## Sources

Skills can be sourced from supported local or Git-based locations. SkillDock records source information so managed skills can later be checked or refreshed.

Source validation is intended to reduce accidental replacement from an unexpected path/source. You should still review third-party skill content before installing it because agent instructions can influence what an AI coding tool does.

## Registry

SkillDock includes registry-style search/install support so reusable skills can be discovered without manually copying directories.

The registry is a distribution convenience, not a trust guarantee. Treat third-party skills as code/configuration: inspect them before use.

## Profiles and collections

Profiles let you define groups of skills for different environments.

Example concept:

```text
Web Development
- git-expert
- testing
- accessibility

Unity
- unity-workflow
- csharp-review
- asset-pipeline

Research
- web-research
- source-checking
- report-writer
```

This makes it easier to reproduce a useful agent setup without enabling every skill everywhere.

## Sync and drift detection

After synchronization, SkillDock can compare managed skill content against the library and detect drift.

Typical states include:

- managed and in sync
- managed but modified/drifted
- missing
- unmanaged

Fingerprints are based on SHA-256 content hashes, so verification does not rely only on filenames or timestamps.

## Reproducible lockfile

v0.4.0 adds `skilldock.lock.json` for reproducible skill sets.

Create/update the lockfile:

```bash
python skilllock.py lock
```

Verify the current library:

```bash
python skilllock.py verify --strict
```

Strict mode detects missing, drifted and unlocked skills and returns a non-zero exit status, which makes it suitable for CI or team checks.

Update skills from their recorded sources:

```bash
python skilllock.py update
```

Or update selected skills:

```bash
python skilllock.py update researcher git-expert
```

When a project/team needs exact reproducibility, commit `skilldock.lock.json` with the project.

## Backup safety

Managed replacement/update operations use SkillDock's backup-aware flow so existing content is not silently discarded where the supported workflow can preserve it.

Backups are a safety mechanism, not a substitute for version control.

## Security model

SkillDock itself is local-first, but the content it manages may instruct powerful AI agents.

Important rules:

- inspect third-party skills before installing them
- do not treat registry presence as endorsement
- review source URLs before updating
- keep sensitive credentials out of skill files
- use version control for team-managed skills
- use lockfile verification when exact content matters

## Privacy

SkillDock does not require a hosted SkillDock account or analytics backend for its core library/sync workflow.

Local skill content remains under your control. Network access may occur when you explicitly install/update from a remote Git/source location.

## Current limitations

SkillDock is not yet a universal configuration manager for every AI tool.

Current limitations include:

- agent ecosystems use different file conventions
- some targets may require manual/custom path configuration
- third-party skill quality and safety vary
- automatic conflict resolution is intentionally conservative
- lockfiles verify SkillDock-managed content, not the behavior of the AI model itself
- MCP servers and broader agent configuration are not fully managed yet

## Roadmap

Possible next steps:

- richer marketplace/index metadata
- signed/verifiable skill packages
- MCP server configuration sync
- AGENTS.md / CLAUDE.md-style instruction sync
- project vs global target templates
- team registry support
- diff preview before update/sync
- richer conflict resolution
- desktop GUI

## Version

Current release: **v0.4.0**

## Security

See [SECURITY.md](SECURITY.md).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT
