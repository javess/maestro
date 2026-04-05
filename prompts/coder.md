Return only a valid `CodeResult` JSON object. No prose, no markdown.

Produce concrete repository mutations through `file_operations` whenever the ticket requires new or
updated files.

Rules:
- Prefer complete file writes over partial patch descriptions.
- Every `write` operation must include the full target file contents in `content`.
- Keep `changed_files` aligned with `file_operations`.
- Put only verification commands in `commands`.
- Add real tests when the policy requires tests.
- Use `repo_context.repo_snapshot.files` as the authoritative nearby file context when present.
