# Provider Credentials Runbook

`maestro` currently supports local-development provider credentials through environment variables.

## Supported Local Path

- create a `.env` file next to your config file
- start from `.env.example`
- set `OPENAI_API_KEY` for the OpenAI adapter

`load_config()` loads that `.env` file before validating provider config and does not override
environment variables that are already set by the shell.

## Current Limitations

- `.env` is for local development only
- there is no encrypted or OS-keychain-backed secret storage yet
- there is no multi-user secret management flow

## Future Direction

Secure key storage remains future work. Likely next options are:

- OS keychain integration
- external secret manager support
- encrypted local credential store

Those options should be introduced in a separate bounded step so secret handling can be reviewed
independently from provider runtime behavior.
