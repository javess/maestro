# Prompt Strategy

`STEP-019` refines agent guidance without changing the deterministic controller.

## Layering model

Each runtime role prompt now has two layers:

1. `prompts/<role>.md`
2. `skills/<role>/SKILL.md`

At runtime, `maestro` concatenates the prompt and the matching role skill so provider calls
receive both:

- strict output-contract instructions
- role-specific quality guidance

## Why keep both layers

- `prompts/` stays focused on schema shape and runtime constraints.
- `skills/` stays focused on best-practice guidance for the role.
- Future prompt tuning can change one layer without hiding durable role expectations in code.

## Role focus

- `product_designer`
  - problem framing
  - explicit assumptions
  - testable acceptance criteria
- `ceremony_master`
  - small, dependency-aware tickets
  - clear parallelization guidance
- `coder`
  - minimal repo mutations
  - repo-style preservation
  - concrete validation commands
- `reviewer`
  - correctness and regression focus
  - policy and test-gap enforcement
  - actionable remediation guidance
