# SkillDock

Manage reusable AI-agent skills once and keep installations across coding agents visible and controlled.

## v0.2.0

- Canonical local skill library (`skills/`)
- Configurable Codex, Claude, Cursor, Gemini or custom targets
- Managed installation manifest with SHA-256 fingerprints
- `status` detects synced, drifted, unmanaged, missing and orphaned skills
- `scan` discovers existing target skills without taking ownership
- `sync --dry-run` previews multi-skill deployment
- `adopt` imports an existing agent skill into the canonical library
- Safe uninstall refuses to delete unmanaged skills unless explicitly forced
- Automatic backup before replacement/removal

```bash
python skilldock.py status
python skilldock.py scan
python skilldock.py install git-expert --to codex,claude --dry-run
python skilldock.py sync --to codex,claude
python skilldock.py adopt my-skill --from-target cursor
```

SkillDock never executes skill contents.
