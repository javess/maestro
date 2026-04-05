# Provider Runtime Adapters

`STEP-013J` brings the real provider adapters to the same runtime-ready baseline.

## Adapter strategies

- OpenAI:
  - uses `responses.parse()` when the schema appears compatible
  - skips known-incompatible native schema calls up front
  - falls back to text generation plus JSON extraction
- Gemini:
  - uses the Google Gen AI SDK `generate_content()` API
  - requests JSON output with a schema-aware config
  - falls back to text generation plus JSON extraction
- Claude:
  - uses the Anthropic `messages.create()` API
  - always uses text generation plus JSON extraction for structured outputs

## Shared contract

Every adapter still implements the same provider-neutral interface:

- `generate_text(...)`
- `generate_structured(...)`
- capability reporting
- model metadata reporting
- normalized error mapping

## Why the adapters differ

Providers expose different structured-output features and validation behavior. The adapter layer is
responsible for those differences so the core engine does not need provider-specific branching.

## Current limitation

- Live runtime verification depends on local API keys and installed SDKs.
- Deterministic evals still rely on `FakeProvider`.
