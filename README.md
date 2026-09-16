# SkillDock

Manage reusable AI-agent skills once and sync them across Codex, Claude, Cursor, Gemini and custom targets.

## v0.3.0

- Add skills from a local directory or Git URL with `source-add`
- Validate `SKILL.md` and reject symlink-containing sources before library import
- Search simple local/remote registry JSON files
- Install registry entries into the managed library
- Save named skill profiles/collections and install a whole profile to multiple targets
- Existing drift detection, backups, dry-run sync, adopt and safe uninstall retained

```bash
python skilldock.py source-add my-skill https://github.com/example/skills.git --subdir skills/my-skill
python skilldock.py registry-list registry.json --query git
python skilldock.py registry-install git-expert registry.json
python skilldock.py profile-save dev --skills git-expert,researcher
python skilldock.py profile-install dev --to codex,claude --dry-run
```

Git sources require the `git` executable. Remote registries are plain JSON; no central SkillDock service is required.
