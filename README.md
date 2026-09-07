# Mission Control

A project board for Claude Code with a memory for parked work: every project on hold must record **why it stopped** and **what resumes it** — so nothing quietly dies in a backlog.

> Status: **work in progress** — being dogfooded before first release.

## What it does

- **One board per repo.** Run the board skill inside any repo and it creates `.claude/board/` there — commit it to share with your team, or gitignore it to keep planning private. Nothing is shared across repos.
- **First run does the setup for you.** It explains what a board is, reads your repo's docs (README, CLAUDE.md, roadmaps, plans, TODOs, `docs/`), and proposes cards from anything that looks like a plan — you approve before anything is written. No plan-like docs? You get an empty board and add the first card yourself.
- **Talk to it in plain language**: add, park, resume, ship, drop, note, tick tasks, "what next", "what's stale".
- **Parking is honest.** A parked project requires a reason *and* an unblock. Holds over three weeks get a one-line nag with the way back.
- **Three synced views**: chat output, a `BOARD.md` markdown mirror (pin it as an editor preview tab), and a console-styled kanban web page published as a private Claude Artifact at a stable URL. The web page is optional (`config.web`) and also works straight from disk.
- Optional per-project checklists beneath the single headline next action.

## Install

Two commands and a restart:

```
/plugin marketplace add kyvyas/mission-control
/plugin install mission-control@mission-control
```

1. The first command registers this repo as a plugin marketplace — Claude Code fetches it from GitHub and reads its manifest. (Works as `claude plugin marketplace add …` from the shell too.)
2. The second installs the plugin at the current commit. Choose **user scope** when asked (the default) so it's available in every project.
3. Restart Claude Code.

The skill is `/mission-control:board` — plugin skills are always namespaced, so type `/mi` and let autocomplete finish it. Mostly you won't type it at all: "show the board", "park X — reason", "what next" all work.

### Your first board

`cd` into any repo and run `/mission-control:board`. Since there's no board yet, it will:

1. Explain what a board is, in a few sentences.
2. Read your repo's docs (README, CLAUDE.md, roadmaps, plans, TODOs, `docs/`) and **propose** cards from anything plan-shaped — nothing is written until you approve. Boilerplate-only docs → an empty board and you add the first card.
3. Create `.claude/board/` in your repo — commit it to share the board with your team, or add `.claude/board/` to `.gitignore` to keep planning private — and publish your web board, handing you its private, stable URL.

Everything is yours and local: boards live in your repos, the web page is published privately to your Claude account. Nothing is shared with the author or anyone else.

**Requirements**: Claude Code with git available. If your environment can't publish Claude Artifacts, the web board turns itself off and chat + `BOARD.md` work as normal.

### Installing from a local clone

No GitHub needed — the repo directory *is* the plugin:

```
claude plugin marketplace add /path/to/mission-control
claude plugin install mission-control@mission-control
```

## Updating

There's no auto-update: the version is the git commit you installed, and every push to `main` is a release. To pick up the latest:

```
claude plugin marketplace update mission-control
claude plugin update mission-control@mission-control
```

then restart Claude Code (or `/reload-plugins`). `claude plugin list` shows which commit you have. To remove: `claude plugin uninstall mission-control@mission-control`.

## Local development

```
claude --plugin-dir .
```

Then `/reload-plugins` after edits, and `claude plugin validate .` before release.

## Layout

- `skills/board/SKILL.md` — the skill; the whole product logic lives here as instructions.
- `templates/board.html` — the web-board template. Every board's `board.html` is regenerated from it on each change, so design updates reach existing boards automatically.
- `templates/board.json` — the starter data file (schema version 1).
- `.claude-plugin/` — plugin manifest and the single-plugin marketplace.

## Data

Each board is a directory `<repo>/.claude/board/`:

| File | Role |
|---|---|
| `board.json` | Source of truth. Yours to edit, commit, or ignore. |
| `BOARD.md` | Markdown mirror, regenerated on every change. |
| `board.html` | Web view, regenerated from the plugin template on every change — never hand-edit. |

Dates are absolute (`YYYY-MM-DD`). Statuses: `idea · active · parked · shipped · dropped`.
