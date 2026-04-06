# Patch Editing Runbook

Use patch operations when `maestro` needs to update an existing file narrowly and preserve nearby
code.

## Expected coder behavior

For existing files, prefer `FileOperation(action="patch")` over `write` when the change is local:

- replace one expression or block
- insert a helper near an existing function
- add a small configuration stanza
- update a test assertion in place

Use `write` for:

- new files
- full rewrites that are genuinely simpler than anchored patching
- generated files where preserving nearby edits is not valuable

## Hunk types

- `replace`
  - swaps the matched anchor text with `content`
- `insert_before`
  - inserts `content` immediately before the anchor
- `insert_after`
  - inserts `content` immediately after the anchor

## Failure handling

Patch failures are explicit. The workspace raises `WorkspaceEditError` when:

- the target file does not exist
- the anchor text cannot be found
- the requested occurrence is invalid

This is intentional. The repair loop added in later steps should use these failures as structured
feedback rather than silently broadening the mutation.

## Validation coverage

`STEP-023` is covered by:

- `tests/test_workspace.py`
  - patch application success and missing-anchor failure
- `tests/test_engine.py`
  - end-to-end engine sync of patch operations back into the target repo

For quick local validation:

```bash
TMPDIR=/var/tmp uv run pytest --no-cov --basetemp=/Users/javiersierra/dev/maestro/.maestro/pytest-temp tests/test_workspace.py tests/test_engine.py
uv run ruff check src/maestro/schemas/contracts.py src/maestro/core/workspace.py prompts/coder.md skills/coder/SKILL.md tests/test_workspace.py tests/test_engine.py
uv run ty check
```
