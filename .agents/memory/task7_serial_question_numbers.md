# Task 7 — serial numbers for Ozon main and follow-up cards

- User specified the display pattern `1. Вопрос`, `2(1). Уточнение`,
  `3(1). Уточнение`, `4. Вопрос`: one sequence for all cards, with the main
  question's current number in parentheses on each follow-up.
- Numbered all eight Ozon HTML pages. Each topic starts at 1; `index.html`
  runs continuously across the six theory sections. Practice retains the
  `Задача` label on main cards so its timer keeps a meaningful label.
- Totals: summary 421 cards; theory topics 67, 118, 151, 46, 33, 6;
  practice 84. Existing IDs, parent references, answer text, compiler links,
  question colors and main/secondary counts were preserved.
- Read-only verification checked consecutive numbers, correct parent number
  in every secondary card, balanced div/details tags, existing local link
  targets and identical title/order between summary and theory topic pages.
- Previous numbering attempt stopped after two failed checks; the user then
  explicitly changed the required numbering and authorized the new direction.
  Task 2 interview browser probe remains STOPPED independently.
- Standard `docs/build_html_site.js` and virtualenv validator remain
  unavailable in this checkout; no repeated attempts were made.
