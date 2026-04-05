# Provider Credentials Runbook

`maestro` currently supports local-development provider credentials through environment variables.

## Supported Local Path

- create a `.env` file next to your config file
- start from `.env.example`
- set any provider keys you plan to use:
  - `OPENAI_API_KEY`
  - `GEMINI_API_KEY`
  - `ANTHROPIC_API_KEY`

`load_config()` loads that `.env` file before validating provider config and does not override
environment variables that are already set by the shell.

## Runtime Support

- OpenAI: runtime wired for text and structured generation with native-schema preflight plus
  fallback parsing.
- Gemini: runtime wired through the Google Gen AI SDK with JSON-schema generation plus fallback
  parsing.
- Claude: runtime wired through the Anthropic SDK with text generation plus JSON extraction for
  structured outputs.

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
