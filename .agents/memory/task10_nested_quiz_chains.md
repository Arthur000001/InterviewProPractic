# Task 10 — Ozon theory follow-ups and grouped modes

- User asked to nest theory follow-up dropdowns in their main answer, as on
  practice, and to make a quiz main question complete only after every
  follow-up is answered correctly. A later request applied one shared timer
  and one final grade to each main-plus-follow-ups interview round.
- Moved 319 unique theory follow-ups in six topic pages and the same 319 in
  `index.html` into `theory-followups` containers at the bottom of each main
  answer. Only the seven theory pages use the new local CSS asset.
- Updated shared quiz code with a grouped path enabled only on pages with
  `theory-followups`. It queues main groups, advances directly on `Знаю`,
  retries the current step after `Сомневаюсь` or `Не знаю`, and marks the
  group learned only after its final follow-up. Flant's flat path remains.
- Updated interview code with the same Ozon-only grouping. Follow-up prompts
  appear one by one on the current card; the timer starts once for the whole
  group; answer and grading controls are available after all prompts.
- Validated seven HTML pages with balanced div/details tags and every nested
  card under its matching main answer. Existing 102 main and 319 secondary
  theory cards and their serial numbers remain. Summary/topic order and
  relative links match. Node syntax checks passed for both scripts.
- Headless Chrome fixture passed quiz sequence: main → first follow-up →
  `Сомневаюсь` repeats it → next follow-up → completed result.
- The older task2 end-to-end browser interview probe remains STOPPED after
  two failed attempts; no third interview browser run was performed.
- Task9 transfer/code-copy work is separately STOPPED, unchanged by this task.
