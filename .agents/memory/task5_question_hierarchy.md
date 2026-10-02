# Task 5 — Ozon question hierarchy

- User asked for archive main questions to be red and supplemental/follow-up
  questions to become separate secondary cards rather than answer text.
- Changed 8 Ozon HTML pages: 102 theory main cards, 35 practice main cards
  now use `key-question`. Topic main numbering remains local; summary
  main numbering remains global. Later, numbering was changed to cover every
  card; see task7_serial_question_numbers.md.
- Converted all 273 items from the previous `follow-up-list` blocks into
  `standard-question secondary-question` cards. The earlier misplaced
  fork/epoll follow-ups now sit under the OS syscall question rather than SQL.
- Moved explicit archive Q/A pairs into secondary cards with their answers;
  handled list-style and one malformed code-block set of supplemental
  questions manually. Later, all 273 cards that initially linked to their
  parent received direct answers; see task6_followup_answers.md.
- Live counts: summary 102 main + 319 secondary; six topic pages together
  102 main + 319 secondary; practice 35 main + 49 secondary.
- Verification: balanced div/details nesting, matching summary/topic titles
  and supplemental questions, intact numbering, all 273 former list items
  represented, parent anchors valid, and local links exist. A headless Chrome
  screenshot confirmed adjacent red main and blue secondary cards. All page
  headers now show the current main/secondary counts. No visible
  `Дополнительные вопросы` or old `follow-up-list` remains.
- Standard `docs/build_html_site.js` and virtualenv validator remain
  unavailable in this checkout; no repeat attempt was made. Task 2's
  end-to-end interview browser probe remains STOPPED after two failures.
