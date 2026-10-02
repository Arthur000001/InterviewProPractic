# Task 9 — STOPPED after two failed attempts

- Objective: move duplicate practice datafix to its existing database card,
  move hash-table and LRU cards with their follow-ups into Go theory and
  summary, repair the broken SQL schema example in practice/database/summary,
  and add copy buttons to Ozon code blocks.
- Targets: eight `.notes/companies/ozon/*.html` pages, plus two new local
  helper assets under `.notes/`.
- Inspected: the datafix already exists as a main database question and in
  summary; the practice copy has a PostgreSQL editor link and four nested
  follow-ups. Hash-table and LRU are currently practice tasks; LRU has four
  nested follow-ups. The SQL schema is split into text plus code windows
  showing only closing parentheses in three pages.
- Applied: created `.notes/ozon_code_copy.js` and
  `.notes/ozon_code_copy.css`. They are not linked from any HTML page and
  have no effect yet. No HTML page was changed.
- Attempt 1: dry-run of `/tmp/interviewpro_task6_reorganize.py` exited at
  `assert len(practice_cards) == 35` (line 70). No page writes happened.
- Attempt 2: read-only diagnostic Python one-liner failed with
  `NameError: name 'HTMLParser' is not defined`, due to the diagnostic's
  temporary namespace. No page writes happened.
- Subsequent read-only evidence: `rg` counts 35 distinct key-question IDs
  in practice. Code inspection shows `MainCards(practice).cards` is accessed
  without calling `feed(practice)`, so its map is empty. The same omission
  also affects helper calls in the draft script. This is a concrete fix to
  make before any approved next run.
- Status: STOPPED under the two-attempt rule. Do not patch or rerun the
  transfer without the user's explicit decision. Task 2's older interview
  browser probe is separately STOPPED and must not be resumed here.
