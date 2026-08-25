---
name: board
description: Project board ("Mission Control"). Use when the user runs /board or asks to show, add, park, resume, ship, drop, tick, or annotate a project, or asks what's parked / what to work on next. Boards are discovered per-repo, with a global fallback.
---

# /board — Mission Control project boards

## Board discovery (do this first, every invocation)

A **board** is a directory holding `board.json` (source of truth) + `BOARD.md` (markdown mirror) + `board.html` (web view, published as an Artifact). Resolve the board for cwd in this order:

1. **In-repo board** — `<repo root>/.claude/board/` in the current git repo. For users who want the board versioned with (or gitignored inside) their repo.
2. **Registry-linked board** — the global board's `config.boards[]` registry maps repo paths to board dirs stored under `~/.claude/board/boards/<slug>/`. Same per-repo scoping, but the repo itself stays untouched (nothing to commit, nothing on GitHub). Each entry: `{name, repo, dir}` — match when cwd is inside `repo`.
3. **Global board** — `~/.claude/board/`. Used when neither of the above matches. Home of non-repo projects.

Whichever matches IS the board: all reads/writes target it, and nothing from other boards is ever shown unless explicitly asked.

- In a git repo with **no** board, don't dump the global board: ask whether to (a) create a board for this repo — and ask where its data should live: linked from `~/.claude/board/boards/<slug>/` (repo untouched — default) or in-repo at `.claude/board/` (committed or gitignored, their call); (b) track this repo as a single project on the global board; or (c) just show `/board all`.
- **`/board all`** — aggregate the global board + every registry/in-repo board it knows, grouped under each board's `config.name`. Only on explicit request.
- When creating a new board, copy `board.html` from an existing board (keep the design; swap only the data blob), set a distinct `config.name` (e.g. "<Repo> Mission Control"), leave `artifactUrl` null until first published, and add a registry entry (in-repo boards get one too, with `dir` inside the repo).

## board.json schema

`config`: `name`, `favicon` (🚀), `artifactUrl` (stable Artifact URL or null), `htmlPath`/`markdownPath` (relative to the board dir), and on the global board `boards[]` (registry).

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

All commands target the discovered board; project references are fuzzy-matched within it (ask if ambiguous).

- **`/board`** (no args) — show the board in chat: sections in order 🔵 Ideas / 🟢 Active / 🚀 Shipped / 🟡 Parked (Dropped only if non-empty); parked items show days parked + the unblock; checklists render as `- [x]`/`- [ ]` with a `(done/total)` count. If anything is parked > 21 days, lead with a one-line nag naming the longest hold and its way back (consider only this board). On a repo board, end with "`/board all` for every board".
- **add** — new project on the discovered board. Infer or ask area + status; active/idea items need a `next_action`.
- **park <project> — <reason>** — status `parked`, `parked_since` = today. **A parked project MUST have both `parked_reason` and `unblock`** — if no unblock was given, ask "what would resume this?" before parking.
- **resume <project>** — status `active`, clear parked fields (keep a note like "parked 2026-08-17 → 2026-09-02: <reason>"), set a fresh `next_action` seeded from the old `unblock`.
- **ship <project>** / **drop <project>** — set status + `shipped_on`/note.
- **note <project> <text>** — append to `notes`.
- **task <project> <text>** — append open task(s) to `tasks` (create the array if absent). To draft a checklist from the repo's plan docs (e.g. `docs/<x>-plan.md`), read them and propose tasks for approval before saving.
- **tick <project> <task>** / **untick** — fuzzy-match the task; set `done` + `done_on` = today (or clear both). Completing the whole checklist: say so and ask whether to ship — never auto-ship.
- **what next / what's stale** — recommend from this board's data: active items' next actions first, then oldest-parked with its unblock.

## Invariants

- Dates are absolute `YYYY-MM-DD` (convert "last week" etc. at write time). Set `updated` on every change; derive all counts from `projects[]`, never cache them.
- `next_action` stays the single headline step; `tasks` is the optional breakdown beneath it — omit the array entirely for projects without a checklist.
- Never invent status changes or tasks the user didn't state.

## After ANY data change — refresh the changed board's three displays

1. Write the change to that board's `board.json`.
2. Regenerate its `BOARD.md` (header tally + longest-hold callout + the section order above).
3. Update its `board.html`: replace **only** the `const BOARD = {...}` blob between `// BOARD-DATA-START` and `// BOARD-DATA-END` (set `updated`; `board` = short board tag, e.g. "Babble", null on the global board; strip per-project `created`/`updated` — the renderer ignores extras). Never touch markup/CSS/renderer.
4. Republish via the Artifact tool: `file_path` = the board's `board.html`, `url` = its `config.artifactUrl`, favicon from config. If `artifactUrl` is null, publish fresh and store the returned URL in config. Each board has its own artifact — never publish one board's data to another board's URL. If publishing fails, still report the data change as done and mention the web board didn't update.
5. Confirm in chat with a one-line summary + that board's URL.

Read-only invocations (plain `/board`, "what next", `/board all`) don't republish.
