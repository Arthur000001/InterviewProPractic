# Task 3: archive audit, 2026-09-28

Scope: read-only review of `.notes/.info/archive` (7 files), local Ozon pages.

- Both 40-page PDFs contain the original Ozon taskbook; the version without the
  sidebar was the source for the earlier 63-card import.
- The two `Вопросы...docx` files have the same 107 main question texts. The
  `000` variant numbers items 91–107; the other variant omits those prefixes.
  Items 1–90 were mapped to existing topic/practice cards by source ID or
  equivalent original question. Items 91–107 were checked individually:
  91/94/96/101/104/106 received new cards, 102 received an experience card,
  and 92/93/95/97/98/99/100/103/105/107 were already represented or were
  equivalent to an existing question. The supplemental PostgreSQL-experience
  question received its own card.
- The long question file contains 263 explicit follow-up questions (lines
  ending in `?` under “Доп. вопросы”). Every one appears in the relevant
  topic/practice answer. The source also has misplaced fragments under several
  SQL items; those non-question fragments were not copied as questions.
- The two `ЗАДАЧИ ОЗОН` DOCX versions contain the same 28 numbered tasks;
  `000` reorganizes them into sections. Tasks 3 (chat schema), 4 (grouping),
  17 (Go interface assertion), 20 (closure) and 22 (SQL JOIN/ban) were present
  only as theory or embedded answers and were copied into Practice. The
  datafix scenario from long-question item 37 was also copied to Practice.
- The supplemental DOCX has 12 media PNGs (14 drawing references). All 12
  were visually inspected: slice/map/string/worker/zip/unique-number code,
  SQL grouping/JOIN and one commentary screenshot. Their actual tasks are
  represented in Practice; the commentary screenshot adds no task.

Applied counts: 102 theory cards in six topics, 35 practice cards.
Verification: local 1-based topic numbers, global 1–102 in summary, practice
1–35, summary/topic title alignment, all 263 follow-ups present, 201 local
references resolve. Chrome screenshot rendered the new back-to-top button.
One attempt to test its click via Chrome DevTools failed before navigation:
`Chrome DevTools port unavailable`. Click behavior remains unverified by that
probe. This is separate from task 2's stopped interview browser probe.

Standard `docs/build_html_site.js` and `.agents/venv/bin/python` checks were
known unavailable before this task; they were not retried. The task 2 HARD STOP
on the summary/interview end-to-end browser probe remains in force.
