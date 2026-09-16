# SkillDock

Manage reusable AI-agent skills/prompts once and sync them into multiple coding-agent folders.

## Features

- Local skill library (`skills/`)
- Configurable targets for Codex, Claude, Cursor, Gemini or any custom agent
- Install one skill to one or many agents
- Diff installed copy vs library
- Backup before overwrite
- List skills and targets
- Zero dependencies

## Quick start

```bash
python skilldock.py init
python skilldock.py list
python skilldock.py install git-expert --to codex,claude
python skilldock.py diff git-expert --to codex
```

Edit `skilldock.json` to match your own agent directories.
