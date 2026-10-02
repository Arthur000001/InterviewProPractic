# Proposed SQL editor link for Ozon Practice

Status: superseded by the user's explicit approval and direct-editor requirement.
Applied implementation: [task4_compiler_links.md](task4_compiler_links.md).

Target: `.notes/companies/ozon/topic_05_practice.html`, task cards 29–33.

Exact addition: a `PostgreSQL db<>fiddle` button on each card, opening
`https://dbfiddle.uk/` in a new tab. db<>fiddle currently provides a PostgreSQL
engine. The button would use the existing `.playground-btn` class, so the
practice countdown starts with the task's badge time as on Go tasks.

Prepared behavior: clicking copies task-specific starter SQL to the clipboard;
the user pastes it into db<>fiddle. The site will not post any SQL or create
public share links automatically. Starter material:

- 29: `orders(user_id, amount)` and sample purchases, plus a blank GROUP BY / HAVING query.
- 30: schema-writing prompt for `users`, `chats`, `messages`, `user_chats`.
- 31: `orders(user_id, price_total)` and five sample rows from the task.
- 32: `users`, `purchase`, `ban_list` tables and the sample rows from the task.
- 33: small illustrative table and a comment that it cannot reproduce the
  locking and scale of a billion-row production datafix.

Affected external target: `dbfiddle.uk` only on a user click/paste/run. Its
site says submissions are licensed under CC0, so no archive answer or user
data should be submitted automatically. No dependency, backend, or network
call from the local static pages would be added.

Go tasks 34–35 have already received buttons for the project's existing
Go Playground provider and local starter code copied on click. Their complete
starter programs are also available in expandable answer sections. The Go 34
starter was run locally; Chrome rendered both starter sections. This plan is
only for the new SQL provider.
