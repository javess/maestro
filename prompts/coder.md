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
- Preserve the existing repo style and avoid unnecessary rewrites.
- Prefer the smallest implementation that satisfies the ticket acceptance criteria.
- Add or update tests close to the changed behavior.
- Keep validation commands deterministic and repo-local.
- Use notes for risks, follow-ups, or assumptions that reviewers should see.
