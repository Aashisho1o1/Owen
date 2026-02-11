# PR Breakdown Plan

## PR 1 — Delete Unused Code / Dead Files
- Remove debug prints, unused vars, stale comments, dead helper blocks.
- Keep behavior identical; compile/lint sanity after each deletion batch.

## PR 2 — Duplicate Logic Removal / Shared Utilities
- Unify client IP parsing and error response payload construction in backend.
- Unify frontend token lifecycle into single `tokenStore` used by context/client.

## PR 3 — Type Safety Hardening (Python + TS)
- Remove TypeScript `any` from API contracts and contexts.
- Narrow broad `except Exception` blocks to expected exception types where possible.

## PR 4 — Tests and Edge-Coverage Baseline
- Add backend API tests for auth, rate-limit failure modes, and error-shape consistency.
- Add frontend unit tests for token store/interceptor behavior and key hooks.

## PR 5 — Performance & Cycle Time Improvements
- Split god modules/hooks; reduce context churn and event fanout.
- Streamline chat streaming updates and trim noisy logging.