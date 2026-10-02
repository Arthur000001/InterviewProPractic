# Task 11 — scrollable quiz history

- User requested that each follow-up appear below the previous question in
  the quiz, with the scroll position moved to the latest step. Earlier steps
  must remain available by scrolling up, showing their answers but no old
  rating buttons.
- Updated the Ozon grouped quiz view to render completed steps as read-only
  question-and-answer sections above the active step. The active step alone
  has reveal and rating controls. Flant's flat quiz view remains unchanged.
- Added one vertical scroll region for the full chain; expanded answers no
  longer create a nested vertical scrollbar. New steps and revealed answers
  scroll to the bottom synchronously. The view does not force the scrollbar
  back down after a manual upward scroll.
- Chrome fixture passed: main answer remains in history, no old buttons,
  automatic scroll to follow-up, manual upward scroll persists, `Сомневаюсь`
  retries the same follow-up, and the group completes after the last one.
- The first browser check found a scroll timing issue; one code correction
  followed, and the second browser check passed. No further attempts needed.
- JS syntax and Ozon page numbering/link structure passed. Task9 and the
  older task2 interview browser probe remain STOPPED independently.
