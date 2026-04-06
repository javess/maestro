# Diff Approval Runbook

Use diff approval when you want a human to inspect generated repo changes before they are synced
and committed into the target repo.

## Policy switch

Enable the gate with:

- `require_diff_approval: true`

The shipped `strict` and `security_sensitive` policies now enable it by default.

## Artifacts and state

When the gate triggers, inspect:

- `TICKET-ID_diff_N.json`
- `TICKET-ID_coder_attempt_N.json`
- `TICKET-ID_checks_N.json`
- `TICKET-ID_reviewer_N.json`
- `RunState.diff_approval_request`

## CLI actions

From the target repo:

```bash
maestro status --repo .
maestro approve <RUN_ID> <TICKET_ID> --repo .
maestro reject <RUN_ID> <TICKET_ID> --repo . --comment "too broad"
maestro rerun <RUN_ID> <TICKET_ID> --repo . --comment "split into smaller edits"
```

Approve finalizes the repo changes. Reject and rerun both create repair context for the next
attempt.
