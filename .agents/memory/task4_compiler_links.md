# Task 4 — direct compiler links

- User rejected the previous copy/paste and nested-code-card behavior for Go
  tasks 34–35, and authorized completing the missing SQL task links.
- Replaced empty Go Playground links for tasks 27, 28, 34, 35 with saved
  `go.dev/play/p/{id}` links containing the task code. Removed
  `.notes/practice_playground.js`, its CSS, status message, and script reference.
- Added PostgreSQL `dbfiddle.uk/{code}` links for tasks 29–33. Saved fiddles
  contain task-specific synthetic data and editable query prompts. Task 33
  states that the small model cannot simulate production-scale locking/load.
- All buttons retain `.playground-btn`, so the existing task timer starts.
- Verification: fetched four saved Go sources and compared exact text; fetched
  five saved SQL fiddles and verified every submitted batch. Static check
  found 35 numbered tasks with direct editor links, 25 existing local refs,
  and no generated starter cards.
- `docs/build_html_site.js` does not exist; `.agents/venv/bin/python` was
  previously found non-executable. The repository's prescribed build/link
  validator cannot run in this checkout; custom structural checks were used.
- Task 2 interview-flow browser probe remains STOPPED after two failed
  attempts; this task did not retry it.
