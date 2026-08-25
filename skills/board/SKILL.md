---
name: board
description: Project board ("Mission Control") for the current repo. Use when the user runs /board or asks to show, add, park, resume, ship, drop, tick, or annotate a project, or asks what's parked / what to work on next. A repo with no board gets one created on first run, seeded from its docs.
---

# /board — Mission Control project board

## The board

Every repo has at most one board: the directory `<repo root>/.claude/board/` holding `board.json` (source of truth) + `BOARD.md` (markdown mirror) + `board.html` (web view — a derived file, regenerated from the plugin template on every refresh, never hand-edited; published as an Artifact only when `config.web` is true). Outside a git repo, use `<cwd>/.claude/board/`. That directory is the only thing any command reads or writes — nothing is shared across repos.

If the directory doesn't exist → **First run**.

## First run — creating the board

Do this in one exchange, not a questionnaire:

**1. Explain, briefly.** Three or four plain sentences, in your own words: a board is a set of project cards in *Ideas · Active · Shipped · Parked*; each active card carries one next action and an optional checklist; parking a card always records *why it stopped* and *what resumes it*, so nothing dies quietly in a backlog. Then the displays: the data lives in `.claude/board/board.json` in this repo (commit it to share with the team, or add `.claude/board/` to `.gitignore` to keep it private — mention this, don't ask), mirrored to a `BOARD.md` they can pin in their editor, plus an optional **web board** — a console-style page published as a Claude Artifact, private to them by default at one stable URL that updates after every change, shareable with teammates if they choose. It's on by default; say "no web board" to skip it (the same page still works locally: `open .claude/board/board.html`). If the Artifact tool isn't available in this session, don't offer it — set `config.web` false silently and mention the local file instead.

**2. Seed from the repo's docs.** Look for planning material: `README.md`, `CLAUDE.md`, `ROADMAP*`, `PLAN*`, `TODO*`, `CHANGELOG*`, `docs/**/*.md` (skip `node_modules`, build output, vendored code). Pull out anything that reads as a project or a plan: roadmap items, "next steps", known gaps, planned features, checklists, follow-ups. Draft cards from them — title, area, a status guess (`idea` unless the doc says it's in progress), `next_action`, `tasks` from checklist-style items, and a `notes` entry naming the source file — and **show the draft for approval before writing anything**; the user can trim, merge, or reject. If the docs hold nothing plan-like, say so in one line and create the board empty: "Nothing to seed from — add your first card with `/board add <project>`."

**3. Create the board from the plugin's templates.** Templates live at `<plugin root>/templates/`; the plugin root is two levels above this skill's base directory (the path in the invocation header) — **resolve symlinks first** (`realpath`), since during development the skill is symlinked in from the repo.
- `board.json` ← `templates/board.json`, with `config.name` = "<Repo> Mission Control", `favicon` 🚀, `web` true unless declined/unavailable, `artifactUrl` null until first published.
- Write the approved cards, then run the **refresh** steps at the end of this file — they produce `BOARD.md` and `board.html` (the first publish returns the artifact URL — store it in config and show it).

## board.json schema

Top level: `version` (currently `1`; a file with no `version` is treated as 1 and gets the field added on its next write), `config`, `projects[]`.

`config`: `name`, `favicon` (🚀), `web` (publish the web board? default true; a file without it is treated as true), `artifactUrl` (stable Artifact URL or null), `htmlPath`/`markdownPath` (relative to the board dir).

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
- **open** / **open the board** — open the web board: `open <config.artifactUrl>` (macOS; `xdg-open` on Linux). Only fall back to the local `board.html` when `config.web` is false or there's no URL yet, and say which one you opened.
- **web board on / off** — set `config.web`. Turning on publishes fresh (or to the stored `artifactUrl` if one exists) and shows the URL. Turning off stops publishing; keep `artifactUrl` (the page keeps serving its last version — artifacts can't be deleted from here, say so) and mention the local file.
- **seed** / **import from docs** — re-run First run step 2 on an existing board (propose, then write only what's approved; never duplicate cards that already exist).

## Invariants

- Dates are absolute `YYYY-MM-DD` (convert "last week" etc. at write time). Set `updated` on every change; derive all counts from `projects[]`, never cache them.
- `next_action` stays the single headline step; `tasks` is the optional breakdown beneath it — omit the array entirely for projects without a checklist.
- Never invent status changes or tasks the user didn't state. Seeded cards are proposals until approved.

## After ANY data change — refresh the three displays

1. Write the change to `board.json`.
2. Regenerate `BOARD.md` in exactly this shape (same on every board, so it's diffable and pinnable):

   ```markdown
   # <config.name> — project board

   _Updated 2026-08-25 · 2 ideas · 1 active · 1 shipped · 3 parked_        ← only non-zero counts; "empty" if none

   > 🟡 **Longest hold:** <title> — since 2026-08-13. Clearance to resume: <unblock>   ← only if something is parked

   ## 🔵 Ideas                                    ← then 🟢 Active · 🚀 Shipped · 🟡 Parked · ⚫ Dropped (Dropped only if non-empty)

   ### <title> `<area>`                           ← idea/active. Shipped: "### <title> — shipped <date>". Parked: "### <title> — parked since <date>"
   **Next:** <next_action>                        ← parked cards instead get "**Why:** <parked_reason>" + "**To resume:** <unblock>"
   **Checklist (1/3):**                           ← only if tasks exist
   - [x] <task> (2026-08-25)
   - [ ] <task>
   - <note>                                       ← one bullet per note, after the checklist

   _nothing here_                                 ← for an empty section
   ```
3. **Regenerate `board.html` from the plugin template** — never patch the existing copy. Read `<plugin root>/templates/board.html` (path rule in First run step 3), set its `<title>` to `config.name`, and replace the `const BOARD = {...}` blob between `// BOARD-DATA-START` and `// BOARD-DATA-END` with this board's data (`updated`; `board` = a short tag for the header, e.g. the repo name; `projects` minus per-project `created`/`updated` — the renderer ignores extras). Write the result over the board's `board.html`. Because the file is rebuilt from the template every time, plugin design updates reach every board on its next refresh, and any hand edits to a board's `board.html` are lost by design.
4. **Only if `config.web` is true** (skip silently otherwise — no nag): republish via the Artifact tool. **First, if `artifactUrl` is set and this session hasn't yet published to it (or another session may have since), sync with the live version before publishing** — the tool refuses to overwrite a version this session hasn't seen, and the refusal shows the user a red error. The sequence that satisfies it: `action: "read"` on the URL; if the result says the version "counts as viewed only once you have Read every line" of a saved file, Read that whole file (one Read call, no offset/limit), then `action: "read"` once more. Since `board.json` is the source of truth, the live page never needs merging — just rebuild from the template and publish. Don't narrate any of this. Then publish: `file_path` = `board.html`, favicon from config, and **always `url` = `config.artifactUrl` when it is set** — publishing without `url` mints a second artifact (the tool keys on file path, so a moved board silently duplicates). Only when `artifactUrl` is null: publish fresh and store the returned URL in config. If the returned URL ever differs from `config.artifactUrl`, that's a duplicate: say so, keep publishing to the stored URL, never to the new one. If publishing fails or the Artifact tool isn't available, still report the data change as done and mention the web board didn't update.
5. Confirm in chat with a one-line summary + the board's URL (or no URL when the web board is off).

Read-only invocations (plain `/board`, "what next") don't republish.
