# Skill: state-and-decisions
## STATE.md (handoff; OVERWRITE, stay <= 80 lines)
Update at the end of EVERY session, even a failed one:
- Last updated, Last commit
- Now: current phase, status, Next action (one specific sentence another agent can execute cold)
- Phase tracker row for this phase
- Verified facts: fill UNKNOWNs ONLY after inspecting (H10)
- Environment: data source, LENS_DATA_ROOT, commands that work
- Open issues / blockers
## DECISIONS.md (APPEND only; <= 6 lines per entry)
Log: any choice between options, any deviation from PHASES.md, any bug found + fix,
any surprising result, any change of default. Format: ### D-0XX | phase N | date | LOCKED?
with Decision / Options / Why / Impact-undo. Never edit old entries; add one that supersedes.
Do not change LOCKED decisions without asking the owner (H15).
## Switching agents
The next agent reads AGENTS.md then STATE.md. If STATE.md is stale or vague, the previous agent failed this rule.
