# Skill: git-checkpoint
## When
- Commit after every finished checklist item.
- Push at every checkpoint (several per phase) and ALWAYS at phase end.
- At phase end also tag: git tag phase-N-done && git push --tags

## Commands
git status --short | head -20          # look first. Anything under data/, models/, *.fits, *.npy, *.pt, *.zip? STOP.
git add -A && git commit -m "phaseN: <what changed, short>"
git push

## Guards
- Refuse to commit any file > 5 MB. Fix .gitignore instead.
- Never force-push. Never rewrite history.
- If push fails (auth/network): note it in STATE.md Open issues, keep committing locally, ask the owner once.
- Commit STATE.md and DECISIONS.md together with the work, so any agent can resume from the repo.
