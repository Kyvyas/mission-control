---
name: board
description: Project board ("Mission Control") for the current repo. Use when the user runs /board or asks to show, add, park, resume, ship, drop, tick, or annotate a project, or asks what's parked / what to work on next. A repo with no board gets one created on first run, seeded from its docs.
---

# /board — Mission Control project board

## The board

Every repo has at most one board: the directory `<repo root>/.claude/board/` holding `board.json` (source of truth) + `BOARD.md` (markdown mirror) + `board.html` (web view, published as an Artifact). Outside a git repo, use `<cwd>/.claude/board/`. That directory is the only thing any command reads or writes — nothing is shared across repos.

If the directory doesn't exist → **First run**.

## First run — creating the board

Do this in one exchange, not a questionnaire:

**1. Explain, briefly.** Three or four plain sentences, in your own words: a board is a set of project cards in *Ideas · Active · Shipped · Parked*; each active card carries one next action and an optional checklist; parking a card always records *why it stopped* and *what resumes it*, so nothing dies quietly in a backlog. Then the displays: the data lives in `.claude/board/board.json` in this repo (commit it to share with the team, or add `.claude/board/` to `.gitignore` to keep it private — mention this, don't ask), mirrored to a `BOARD.md` they can pin in their editor, plus a **web board** — a console-style page published as a Claude Artifact, private to them by default at one stable URL that updates after every change, shareable with teammates if they choose.

**2. Seed from the repo's docs.** Look for planning material: `README.md`, `CLAUDE.md`, `ROADMAP*`, `PLAN*`, `TODO*`, `CHANGELOG*`, `docs/**/*.md` (skip `node_modules`, build output, vendored code). Pull out anything that reads as a project or a plan: roadmap items, "next steps", known gaps, planned features, checklists, follow-ups. Draft cards from them — title, area, a status guess (`idea` unless the doc says it's in progress), `next_action`, `tasks` from checklist-style items, and a `notes` entry naming the source file — and **show the draft for approval before writing anything**; the user can trim, merge, or reject. If the docs hold nothing plan-like, say so in one line and create the board empty: "Nothing to seed from — add your first card with `/board add <project>`."

**3. Create the board from the plugin's templates.** Templates live at `<plugin root>/templates/`; the plugin root is two levels above this skill's base directory (the path in the invocation header) — **resolve symlinks first** (`realpath`), since during development the skill is symlinked in from the repo.
- `board.json` ← `templates/board.json`, with `config.name` = "<Repo> Mission Control", `favicon` 🚀, `artifactUrl` null until first published.
- `board.html` ← `templates/board.html` verbatim; set `<title>` to `config.name`. The data blob is filled in by the refresh step below.
- Write the approved cards, then run the **refresh** steps at the end of this file (the first publish returns the artifact URL — store it in config and show it).

## board.json schema

Top level: `version` (currently `1`; a file with no `version` is treated as 1 and gets the field added on its next write), `config`, `projects[]`.

`config`: `name`, `favicon` (🚀), `artifactUrl` (stable Artifact URL or null), `htmlPath`/`markdownPath` (relative to the board dir).

Per project:

```json
{
  "id": "kebab-slug",
  "title": "Readable name",
  "area": "optional grouping tag",
  "status": "idea | active | parked | shipped | dropped",
  "next_action": "for idea/active — the single next concrete step",
  "parked_since": "YYYY-MM-DD (parked only)",
  "parked_reason": "why it stopped (parked only)",
  "unblock": "what resumes it (parked only)",
  "shipped_on": "YYYY-MM-DD (shipped only)",
  "tasks": [{"text": "one step", "done": false, "done_on": "YYYY-MM-DD (when done)"}],
  "notes": ["short factual notes, absolute dates only"],
  "created": "YYYY-MM-DD",
  "updated": "YYYY-MM-DD"
}
```

## Commands (interpret naturally — intents, not exact syntax)

Project references are fuzzy-matched (ask if ambiguous).

- **`/board`** (no args) — show the board in chat: sections in order 🔵 Ideas / 🟢 Active / 🚀 Shipped / 🟡 Parked (Dropped only if non-empty); parked items show days parked + the unblock; checklists render as `- [x]`/`- [ ]` with a `(done/total)` count. If anything is parked > 21 days, lead with a one-line nag naming the longest hold and its way back.
- **add** — new project. Infer or ask area + status; active/idea items need a `next_action`.
- **park <project> — <reason>** — status `parked`, `parked_since` = today. **A parked project MUST have both `parked_reason` and `unblock`** — if no unblock was given, ask "what would resume this?" before parking.
- **resume <project>** — status `active`, clear parked fields (keep a note like "parked 2026-08-17 → 2026-09-02: <reason>"), set a fresh `next_action` seeded from the old `unblock`.
- **ship <project>** / **drop <project>** — set status + `shipped_on`/note.
- **note <project> <text>** — append to `notes`.
- **task <project> <text>** — append open task(s) to `tasks` (create the array if absent). To draft a checklist from the repo's plan docs (e.g. `docs/<x>-plan.md`), read them and propose tasks for approval before saving.
- **tick <project> <task>** / **untick** — fuzzy-match the task; set `done` + `done_on` = today (or clear both). Completing the whole checklist: say so and ask whether to ship — never auto-ship.
- **what next / what's stale** — recommend from the board: active items' next actions first, then oldest-parked with its unblock.
- **seed** / **import from docs** — re-run First run step 2 on an existing board (propose, then write only what's approved; never duplicate cards that already exist).

## Invariants

- Dates are absolute `YYYY-MM-DD` (convert "last week" etc. at write time). Set `updated` on every change; derive all counts from `projects[]`, never cache them.
- `next_action` stays the single headline step; `tasks` is the optional breakdown beneath it — omit the array entirely for projects without a checklist.
- Never invent status changes or tasks the user didn't state. Seeded cards are proposals until approved.

## After ANY data change — refresh the three displays

1. Write the change to `board.json`.
2. Regenerate `BOARD.md` (header tally + longest-hold callout + the section order above).
3. Update `board.html`: replace **only** the `const BOARD = {...}` blob between `// BOARD-DATA-START` and `// BOARD-DATA-END` (set `updated`; `board` = a short tag for the header, e.g. the repo name; strip per-project `created`/`updated` — the renderer ignores extras). Never touch markup/CSS/renderer.
4. Republish via the Artifact tool: `file_path` = `board.html`, favicon from config, and **always `url` = `config.artifactUrl` when it is set** — publishing without `url` mints a second artifact (the tool keys on file path, so a moved board silently duplicates). Only when `artifactUrl` is null: publish fresh and store the returned URL in config. If the returned URL ever differs from `config.artifactUrl`, that's a duplicate: say so, keep publishing to the stored URL, never to the new one. If publishing fails or the Artifact tool isn't available, still report the data change as done and mention the web board didn't update.
5. Confirm in chat with a one-line summary + the board's URL.

Read-only invocations (plain `/board`, "what next") don't republish.
