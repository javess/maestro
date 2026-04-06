# Benchmark Scoring

`STEP-030` adds a simple benchmark harness that scores end-to-end delivery behavior across fixture
repos.

## Goals

- measure delivery quality across representative repo shapes
- keep benchmark execution deterministic
- provide a CLI-readable and JSON-readable output

## Current benchmark set

The first benchmark scenarios cover:

- a Python fixture repo
- a Node fixture repo
- a broken/generic repo

## Score model

The first score is intentionally simple:

- successful completion score
- specialized-adapter bonus
- retry penalty
- evidence-bundle bonus

This is not a scientific benchmark yet. It is a regression-oriented product scorecard.
