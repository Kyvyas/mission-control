# Mission Control

A project board for Claude Code with a memory for parked work: every project on hold must record **why it stopped** and **what resumes it** — so nothing quietly dies in a backlog.

> Status: **work in progress** — being dogfooded before first release.

## What it does

- `/board` — talk to your board in natural language: add, park, resume, ship, tick tasks.
- **Boards are discovered per-repo**: a repo can have its own board (in-repo or linked from `~/.claude/board/boards/`), with a global board for everything else. `/board all` aggregates.
- **Parking is honest**: a parked project requires a reason and an unblock. Long holds get a gentle nag with the way back.
- **Three synced views**: chat output, a `BOARD.md` markdown mirror (pin it as an IDE preview tab), and a console-styled kanban web page published as a Claude Artifact at a stable private URL.
- Optional per-project checklists (`task` / `tick` / `untick`).

## Install (once released)

```
/plugin marketplace add kyvyas/mission-control
/plugin install mission-control@mission-control
```

## Local development

```
claude --plugin-dir .
```

Then `/reload-plugins` after edits, and `claude plugin validate --strict .` before release.

## Layout

- `skills/board/SKILL.md` — the skill.
- `templates/board.html` — the web-board template (data blob swapped per board between the `BOARD-DATA-START/END` markers).
