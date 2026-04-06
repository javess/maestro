# Observation Loop Runbook

## Where to find generated follow-ups

- `<target-repo>/.maestro/runs/<RUN_ID>/<ticket_id>_observation_followups_<n>.json`

## When follow-ups appear

- failed validation checks
- reviewer issues
- future observation sources as they are added

## How to use them

1. Open the observation artifact after a failed or escalated ticket.
2. Review the normalized `observations`.
3. Review the generated `follow_ups`.
4. Promote the useful items into backlog or Jira-ready planning work.

## Current limitation

- The loop emits structured proposals; it does not yet automatically merge them back into the live
  backlog graph.
