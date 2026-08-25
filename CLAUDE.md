# CLAUDE.md

Guidance for Claude Code working in this repo. Read before editing.

## Project

**Mission Control** is a Claude Code plugin (in development) that gives users project boards with a memory for parked work. Its one opinion: a parked project MUST record *why it stopped* and *what resumes it*, so nothing dies silently in a backlog. Built and dogfooded by `kyvyas` starting 2026-08-25; not yet published.

The plugin ships **logic only**. Board *data* lives in each user's repo at `<repo>/.claude/board/` (committed or gitignored, their choice). This repo's own board is at `.claude/board/` and is gitignored.

## Layout

```
.claude-plugin/
  plugin.json        Plugin manifest. NO version field — deliberate: version derives
                     from git SHA, so installs always update (a set-but-unbumped
                     version silently pins users to a stale release).
  marketplace.json   This repo is its own marketplace (source: "./").
skills/board/
  SKILL.md           The /board skill — the entire product logic lives here as
                     instructions, not code. THIS IS LIVE: ~/.claude/skills/board
                     is a symlink into this directory, so edits here change the
                     author's working /board immediately (next skill invocation).
templates/
  board.html         The web-board template (console design). Every board's
                     board.html is REGENERATED from this file on each refresh
                     (title + `const BOARD = {...}` blob between the
                     `// BOARD-DATA-START` / `// BOARD-DATA-END` markers swapped in),
                     so design edits here reach all boards on their next change.
  board.json         Starter data file (schema `version: 1`, empty projects). New
                     boards are bootstrapped from these two files — the skill finds
                     them at `<realpath of skill dir>/../../templates/`.
```

## Architecture (settled decisions — don't relitigate casually)

- **A board** = `<repo root>/.claude/board/` (cwd if not in a git repo) holding `board.json` (source of truth) + `BOARD.md` (markdown mirror, IDE-pinnable) + `board.html` (web view published as a Claude Artifact at a stable per-board URL held in `config.artifactUrl`; a derived file — rebuilt from `templates/board.html` on every refresh, never hand-edited).
- **One board per repo, nothing else.** No global board, no registry, no cross-repo aggregation — there used to be all three (2026-08-25, day one) and they were dropped for being more muddle than value. Don't reintroduce them; a user who wants planning outside a repo can make a plain directory a board.
- **First run** in an unboarded repo: explain boards + the artifact in a few sentences, mention commit-vs-gitignore (don't ask), seed proposed cards from the repo's docs (README, CLAUDE.md, ROADMAP/PLAN/TODO, docs/) for approval, then bootstrap from `templates/`. Never copy another board's files.
- **Statuses**: `idea | active | parked | shipped | dropped`, displayed in column order Ideas · Active · Shipped · Parked (Dropped only when non-empty). Parking requires `parked_reason` + `unblock`. Holds > 21 days trigger the "longest hold" nag.
- **`next_action` vs `tasks`**: `next_action` is the single headline step; `tasks` is an optional checklist beneath it. Never auto-ship on checklist completion — announce and ask.
- **Three synced displays** per board, refreshed after every data change; chat + BOARD.md are the core, the artifact is an enhancement gated by `config.web` (default true; auto-false when the Artifact tool is unavailable). board.html is always generated so the console view works from disk.

## Design system (templates/board.html)

Console aesthetic, dark-first with a full "daylight ops" light theme (token-level, three-state theme pattern: bare `:root` = dark, `@media (prefers-color-scheme: light)` guarded `:root:not([data-theme="dark"])`, plus `:root[data-theme="light"]`). Fonts: Rajdhani (signage/wordmark), IBM Plex Sans (body), IBM Plex Mono (telemetry). Status colors: idea slate-violet, active GO-green, parked HOLD-amber, shipped steel-blue, dropped grey; `--toggle` turquoise is reserved for the card disclosures (Checklist/Notes caret + hover) — the red `--accent` is the wordmark only. Checklists and notes render inside native `<details>`, collapsed by default. Mission language: callsigns `[PROPOSED] [GO] [COMPLETE] [HOLD] [SCRUBBED]`, `HOLD T+<n>d` chips, "Mission complete" stamps, "clearance to resume" phrasing. Days-parked is computed live in the page from `parked_since` — never bake day counts into the blob.

## Pre-release roadmap

The release checklist lives on this repo's board (`.claude/board/`, "Publish Mission Control as a plugin" card) — that's the source of truth for status. The known gaps, with rationale:

1. ~~**Template-asset bootstrap**~~ — done 2026-08-25: new boards come from `templates/board.{html,json}`.
2. ~~**Schema versioning**~~ — done 2026-08-25: `"version": 1` in the starter; files without it are treated as v1 and stamped on next write.
3. ~~**Re-render from template**~~ — done 2026-08-25: the refresh step rebuilds board.html from the template every time; per-board copies can no longer drift.
4. ~~**Optional artifact**~~ — done 2026-08-25: `config.web` (default true) governs publishing; board.html is still generated locally either way.
5. **Namespacing decision**: installed plugin skills are `/plugin-name:skill-name` → currently `/mission-control:board`. Decide before release (rename plugin or skill if that's too long).
6. **Self-migration test**: the author must uninstall the personal symlinked skill, install the built plugin, and confirm this repo's board still works.
7. **Cold test + validate**: `claude plugin validate --strict .` and a first-run test in a repo that has never seen a board.

## Development

- Run locally: `claude --plugin-dir .` then `/board` (or the namespaced form once installed). `/reload-plugins` picks up edits mid-session.
- Validate before release: `claude plugin validate --strict .`
- `claude plugin eval` exists for eval suites but is early-access; not required for v1.
- The author's live boards during dogfooding: this repo's at `.claude/board/` (gitignored) and Babble's at `~/Desktop/milestones/.claude/board/` (gitignored there too). Useful as real-world test data — but they are the author's real planning data, not fixtures; don't mutate them except through genuine `/board` operations.

## Conventions

- No AI-attribution trailers (`Co-Authored-By` etc.) in commits or PRs.
- Dates in board data are absolute `YYYY-MM-DD`, always.
- In-app copy voice is plain and warm, never quippy; mission-control terminology is flavor on labels, not jokes in content.
- **Maintenance**: when a session adds a dependency, convention, or gotcha, update this file before ending the session and flag the update for review.
