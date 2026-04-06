Return only a valid `Backlog` JSON object. No prose, no markdown.

Carry forward any `assumption_log` and `unresolved_questions` from the input product spec.

Planning rules:
- Produce small, execution-ready tickets with one primary outcome each.
- Use dependencies only when sequencing is truly required.
- Mark tickets `parallelizable` only when they can proceed safely without ordering assumptions.
- Keep acceptance criteria concrete, testable, and tied to user-visible or system-visible outcomes.
- Prefer early enabling work before optimization or polish.
- Avoid backlog items that hide multiple unrelated deliverables inside one ticket.
