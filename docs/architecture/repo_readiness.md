# Repo Readiness

`STEP-027` adds a deterministic support-tier and readiness score on top of repo discovery.

## Purpose

Repo detection alone tells `maestro` what commands and conventions a repo likely uses. It does not
answer whether the repo is a good candidate for autonomous mutation.

The readiness layer makes that explicit with:

- support tier
  - `supported`
  - `experimental`
  - `planning_only`
- readiness score
- blockers
- recommendations

## Signals

The first implementation scores only local, deterministic signals:

- specialized adapter matched
- git repository present
- build commands discovered
- test commands discovered
- lint commands discovered
- guidance richness

This is intentionally conservative and explainable.
