# SkillDock

Manage reusable AI-agent skills once and sync them across Codex, Claude, Cursor, Gemini and custom agents.

## v0.4.0

- Reproducible `skilldock.lock.json` with a SHA-256 content hash for every library skill
- `skilllock.py verify --strict` detects missing, drifted and unlocked skills and exits non-zero for CI
- `skilllock.py update` refreshes skills from their recorded Git/local sources using SkillDock's existing backup-safe source flow
- Lockfile can be regenerated automatically after source updates
- Existing registry search/install, profiles, target sync, drift detection, backups and source validation remain available

```bash
python skilllock.py lock
python skilllock.py verify --strict
python skilllock.py update
python skilllock.py update researcher git-expert
```

Commit `skilldock.lock.json` when you want a project or team to share the exact same skill contents.
