Return only a valid `ProductSpec` JSON object. No prose, no markdown.

Use the normalized `brief` payload to populate:
- `title`
- `summary`
- `problem`
- `target_users`
- `outcomes`
- `scope`
- `non_goals`
- `constraints`
- `risks`
- `assumptions`
- `assumption_log`
- `unresolved_questions`
- `acceptance_criteria`

Design rules:
- Frame the user problem before solution details.
- Prefer concrete outcomes over implementation prescriptions.
- Keep scope intentionally small and testable for the first iteration.
- Capture operational, UX, and delivery risks when they materially affect delivery.
- Do not invent certainty; use `assumptions`, `assumption_log`, and `unresolved_questions`.
- Make acceptance criteria observable and verifiable.
