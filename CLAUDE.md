# CLAUDE.md

Guidance for Claude Code working in this repo. Read before editing.

## Project

**Mission Control** is a Claude Code plugin (in development) that gives users project boards with a memory for parked work. Its one opinion: a parked project MUST record *why it stopped* and *what resumes it*, so nothing dies silently in a backlog. Built and dogfooded by `kyvyas` starting 2026-08-25; not yet published.

The plugin ships **logic only**. Board *data* never lives in this repo — each user's boards live in their own repos or under `~/.claude/board/`.

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
  board.html         The web-board template (console design). Data is embedded as a
                     `const BOARD = {...}` blob between `// BOARD-DATA-START` and
                     `// BOARD-DATA-END` markers; updates swap ONLY the blob.
```

## Architecture (settled decisions — don't relitigate casually)

- **A board** = a directory with `board.json` (source of truth) + `BOARD.md` (markdown mirror, IDE-pinnable) + `board.html` (web view published as a Claude Artifact at a stable per-board URL held in `config.artifactUrl`).
- **Discovery order** (resolved fresh on every `/board` invocation): (1) in-repo board at `<repo>/.claude/board/`; (2) registry-linked board — the global board's `config.boards[]` maps repo paths to dirs under `~/.claude/board/boards/<slug>/`; (3) global board at `~/.claude/board/`. Whichever matches IS the board; **strict scoping** — never show other boards' projects unless the user runs `/board all`. In an unboarded git repo, ask (create / track-on-global / show all); never dump the combined board uninvited.
- **Why two storage homes**: users differ on whether planning data belongs in a product repo. In-repo suits teams (committed, versioned with the code); registry-linked keeps personal planning out of the repo and off GitHub entirely. Both are first-class; registry-linked is the default offer.
- **Install location ≠ data location.** The plugin can be installed at user or project scope; boards materialize wherever the user chooses at first use. Never hardcode `~/.claude` as the data home.
- **Statuses**: `idea | active | parked | shipped | dropped`, displayed in column order Ideas · Active · Shipped · Parked (Dropped only when non-empty). Parking requires `parked_reason` + `unblock`. Holds > 21 days trigger the "longest hold" nag.
- **`next_action` vs `tasks`**: `next_action` is the single headline step; `tasks` is an optional checklist beneath it. Never auto-ship on checklist completion — announce and ask.
- **Three synced displays** per board, refreshed after every data change; chat + BOARD.md are the core, the artifact is an enhancement (see roadmap: it must become optional).

## Design system (templates/board.html)

Console aesthetic, dark-first with a full "daylight ops" light theme (token-level, three-state theme pattern: bare `:root` = dark, `@media (prefers-color-scheme: light)` guarded `:root:not([data-theme="dark"])`, plus `:root[data-theme="light"]`). Fonts: Rajdhani (signage/wordmark), IBM Plex Sans (body), IBM Plex Mono (telemetry). Status colors: idea slate-violet, active GO-green, parked HOLD-amber, shipped steel-blue, dropped grey. Mission language: callsigns `[PROPOSED] [GO] [COMPLETE] [HOLD] [SCRUBBED]`, `HOLD T+<n>d` chips, "Mission complete" stamps, "clearance to resume" phrasing. Days-parked is computed live in the page from `parked_since` — never bake day counts into the blob.

## Pre-release roadmap

The release checklist lives on the author's global board ("Publish Mission Control as a plugin" card) — that's the source of truth for status. The known gaps, with rationale:

1. **Template-asset bootstrap**: SKILL.md still says "copy board.html from an existing board" — a fresh install has none. The skill must bootstrap new boards from `templates/board.html` (+ a starter board.json) inside the plugin, referenced via the skill's base directory.
2. **Schema versioning**: add `"version": 1` to board.json + a migration rule in the skill BEFORE strangers create data files (the schema changed four times on day one).
3. **Re-render from template**: today each board owns a drifting *copy* of board.html; design improvements in plugin updates won't propagate. Switch to re-rendering from the plugin template on each publish.
4. **Optional artifact**: some users lack artifact publishing or don't want a web page. Chat + BOARD.md must work standalone; a per-board config flag governs publishing.
5. **Namespacing decision**: installed plugin skills are `/plugin-name:skill-name` → currently `/mission-control:board`. Decide before release (rename plugin or skill if that's too long).
6. **Self-migration test**: the author must uninstall the personal symlinked skill, install the built plugin, and confirm existing boards still discover.
7. **Cold test + validate**: `claude plugin validate --strict .` and a first-run test in a repo that has never seen a board.

## Development

- Run locally: `claude --plugin-dir .` then `/board` (or the namespaced form once installed). `/reload-plugins` picks up edits mid-session.
- Validate before release: `claude plugin validate --strict .`
- `claude plugin eval` exists for eval suites but is early-access; not required for v1.
- The author's live boards during dogfooding: global at `~/.claude/board/` (holds this plugin's cards), Babble's at `~/.claude/board/boards/babble/` (registry-linked to `~/Desktop/milestones`). Useful as real-world test data — but they are the author's real planning data, not fixtures; don't mutate them except through genuine `/board` operations.

## Conventions

- No AI-attribution trailers (`Co-Authored-By` etc.) in commits or PRs.
- Dates in board data are absolute `YYYY-MM-DD`, always.
- In-app copy voice is plain and warm, never quippy; mission-control terminology is flavor on labels, not jokes in content.
- **Maintenance**: when a session adds a dependency, convention, or gotcha, update this file before ending the session and flag the update for review.
