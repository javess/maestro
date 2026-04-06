# Provider Credentials Runbook

`maestro` supports local-development provider credentials through environment variables, `.env`
files, and OS keychain storage via `keyring`.

## Resolution order

Provider secrets now resolve in this order:

1. shell environment variable
2. `.env` file next to the active config file
3. OS keychain entry managed by `maestro creds`

## `.env` path

- create a `.env` file next to your config file
- start from `.env.example`
- set any provider keys you plan to use:
  - `OPENAI_API_KEY`
  - `GEMINI_API_KEY`
  - `ANTHROPIC_API_KEY`

`load_config()` loads that `.env` file before validating provider config and does not override
environment variables that are already set by the shell.

## Secure keychain path

Store a provider key in the OS keychain:

```bash
uv run maestro creds set openai
uv run maestro creds set gemini
uv run maestro creds set anthropic
```

Inspect whether a secret resolves from the environment or keychain:

```bash
uv run maestro creds status openai
```

Delete a stored secret:

```bash
uv run maestro creds delete openai
```

By default, secrets are stored under the keychain service name `maestro` and the credential name
matching the provider env var, such as `OPENAI_API_KEY`. Both can be overridden with
`--service` and `--credential-name`.

## Runtime Support

- OpenAI: runtime wired for text and structured generation with native-schema preflight plus
  fallback parsing.
- Gemini: runtime wired through the Google Gen AI SDK with JSON-schema generation plus fallback
  parsing.
- Claude: runtime wired through the Anthropic SDK with text generation plus JSON extraction for
  structured outputs.

## Current Limitations

- `.env` is still plain-text and should be treated as a local-development fallback
- secure storage currently depends on the local OS keychain via `keyring`
- there is no multi-user secret management flow
- provider configs still name the expected env var because that remains the fallback resolution key

## Future Direction

Likely next options are:

- OS keychain integration
- external secret manager support
- encrypted local credential store

Those options should be introduced in a separate bounded step so secret handling can be reviewed
independently from provider runtime behavior.
