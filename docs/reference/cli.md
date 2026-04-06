# CLI Reference

## Core commands

```bash
maestro init
maestro discover
maestro plan <brief>
maestro run-ticket <TICKET_ID>
maestro review <TICKET_ID>
maestro status
maestro resume <RUN_ID>
maestro eval
maestro doctor
maestro preview
```

## Credential commands

```bash
maestro creds set <provider>
maestro creds status <provider>
maestro creds delete <provider>
```

## Verbosity

- `-v`: progress-level logs
- `-vv`: maximum request/response and step tracing
- `--log-level DEBUG`: explicit equivalent of the highest verbosity mode

## Common examples

```bash
maestro -vv plan brief.md --config examples/maestro.openai.yaml --repo .
maestro preview --repo . --adapter local --command "python game.py --demo"
maestro status --repo .
maestro eval --json-output-path eval-report.json
```
