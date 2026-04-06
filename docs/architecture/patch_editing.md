# Patch Editing

`STEP-023` adds a patch-oriented mutation layer for coder output so `maestro` can make narrow,
anchored edits to existing files without defaulting to full rewrites.

## Why

Whole-file writes are acceptable for new files and simple examples, but they are a poor default
for real repositories because they:

- overwrite nearby code unnecessarily
- discard formatting and comments around the intended change
- increase the blast radius of model mistakes
- make review diffs harder to trust

The patch-editing layer keeps the existing `CodeResult` contract but extends `FileOperation` with a
`patch` action and explicit `PatchHunk` records.

## Contract

Each patch hunk is typed and validated before execution:

- `kind`
  - `replace`
  - `insert_before`
  - `insert_after`
- `match`
  - required anchor text already present in the target file
- `content`
  - replacement text or inserted text
- `occurrence`
  - 1-based match selection when the anchor appears multiple times

The `FileOperation` invariants are:

- `write` requires `content`
- `patch` requires one or more `hunks`
- `delete` and `patch` reject full-file `content`

## Runtime behavior

Patch application happens inside the repo workspace layer:

1. the target file must already exist
2. each hunk resolves a concrete anchored occurrence
3. the workspace applies hunks in order against the current file content
4. any missing anchor raises an explicit `WorkspaceEditError`
5. the patched file is written back into the isolated workspace and later synced to the target repo
   through the existing review and policy gates

This keeps patch failure explicit and recoverable instead of silently degrading to a rewrite.

## Current limits

The first implementation is intentionally narrow:

- anchors are plain string matches, not AST-aware ranges
- hunks are applied sequentially within one file
- conflicts are surfaced as errors instead of auto-merged
- whole-file writes remain available as a fallback for new files or large rewrites

These limits keep the execution path deterministic while providing a safer mutation primitive for
later repair loops and diff approval workflows.
