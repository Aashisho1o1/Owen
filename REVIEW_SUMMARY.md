# REVIEW SUMMARY

## Scope
- Complete tracked-file pass using static outputs + line-level code inspection for highest-risk modules.
- Static tools attempted: `pytest`, `eslint`, `tsc`, plus grep-driven structural checks.
- Environment limits: `ruff`, `mypy`, `radon`, `bandit` unavailable; `depcheck`/`jscpd` blocked by network policy.

## P0/P1 Findings
### P1 — Security and Reliability
- `backend/routers/indexing_router.py`: internal exception leakage via `detail=str(e)` on many endpoints (L78, L107, L127, L147, L166, L195, L215, L234).
- `backend/middleware/security_middleware.py`: CSP allows `unsafe-inline` scripts (L74), increasing XSS risk.
- `backend/services/infra_service.py`: rate-limiter error path fails open, allowing costly endpoint traffic during limiter outages.
- `frontend/src/App.tsx`: runtime CSS injection with `dangerouslySetInnerHTML` (L57).

### P1 — Correctness and API Contract
- `backend/services/grammar_service.py`: calls `generate_response_async(...)` without matching method implementation in backend services (L445).
- `frontend/src/pages/DocumentsPage.tsx`: references `getRecentDocuments` from `useDocuments`, but hook does not export it (L24, L100).
- `backend/services/auth_service.py`: guest data migration path invoked but left TODO/no-op (L830), creating conversion inconsistency risk.

### P1 — Maintainability / Complexity
- God modules:
  - Backend: `backend/routers/chat_router.py`, `backend/services/database.py`, `backend/services/auth_service.py`, `backend/services/character_voice_service.py`
  - Frontend: `frontend/src/contexts/AuthContext.tsx`, `frontend/src/contexts/ChatContext.tsx`, `frontend/src/hooks/useChat.ts`, `frontend/src/hooks/useDocuments.ts`
- Duplicated token lifecycle logic across `frontend/src/contexts/AuthContext.tsx`, `frontend/src/services/api/client.ts`, `frontend/src/services/api/auth.ts`.
- Duplicated IP parsing logic across `backend/utils/request_helpers.py`, `backend/services/rate_limiter.py`, `backend/middleware/security_middleware.py`.

## Refactor Order (strict)
1. Delete dead code/noise (`print`, unused vars, stale comments, dead helpers).
2. Unify redundancy (token store, client IP helper, error-response shape).
3. Introduce abstractions (split god modules into domain-focused units).
4. Optimize runtime flow (reduce render churn, limit logging, streamline stream updates).
5. Tighten type safety and tests (remove `any`, add targeted unit/integration tests).

## Tool Results Snapshot
- `backend`: `pytest -q --maxfail=1` → no tests found.
- `frontend`: `npx eslint . --ext .ts,.tsx` → 69 errors, 20 warnings.
- `frontend`: `npx tsc --noEmit` → passes in this environment.
- `frontend`: `npm test` → missing script.
- `depcheck`/`jscpd` unavailable due registry/network restrictions.