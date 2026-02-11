# FILE-BY-FILE CODE REVIEW

Static-tool evidence included from: `eslint`, `tsc`, `pytest`, grep-based structural scans.

Python tools unavailable in this environment: `ruff`, `mypy`, `radon`, `bandit` (not installed).

`depcheck` and `jscpd` could not run due restricted network access (npm registry unreachable).

FILE: .claude/settings.local.json

1. Purpose Summary (1 sentence)
   - Structured configuration/data resource used by app/tooling.

2. Requirement Served
   - Supports repository governance, tooling, or deployment reproducibility.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: .codeqlignore

1. Purpose Summary (1 sentence)
   - Repository source/configuration artifact.

2. Requirement Served
   - Supports repository governance, tooling, or deployment reproducibility.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: .gitignore

1. Purpose Summary (1 sentence)
   - Repository source/configuration artifact.

2. Requirement Served
   - Supports repository governance, tooling, or deployment reproducibility.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: .pre-commit-config.yaml

1. Purpose Summary (1 sentence)
   - Project/deploy/tooling configuration.

2. Requirement Served
   - Supports repository governance, tooling, or deployment reproducibility.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: .railwayignore

1. Purpose Summary (1 sentence)
   - Repository source/configuration artifact.

2. Requirement Served
   - Supports repository governance, tooling, or deployment reproducibility.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: .vscode/settings.json

1. Purpose Summary (1 sentence)
   - Structured configuration/data resource used by app/tooling.

2. Requirement Served
   - Supports repository governance, tooling, or deployment reproducibility.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: backend/.env.example

1. Purpose Summary (1 sentence)
   - Repository source/configuration artifact.

2. Requirement Served
   - Supports secure, cost-controlled API delivery for OwenWrites backend features.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: backend/Dockerfile

1. Purpose Summary (1 sentence)
   - Repository source/configuration artifact.

2. Requirement Served
   - Supports secure, cost-controlled API delivery for OwenWrites backend features.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: backend/__init__.py

1. Purpose Summary (1 sentence)
   - Python backend source module.

2. Requirement Served
   - Supports secure, cost-controlled API delivery for OwenWrites backend features.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "except Exception|print\(" backend/__init__.py`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: backend/assets/got_character_profiles.json

1. Purpose Summary (1 sentence)
   - Structured configuration/data resource used by app/tooling.

2. Requirement Served
   - Supports secure, cost-controlled API delivery for OwenWrites backend features.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: backend/config/demo_config.py

1. Purpose Summary (1 sentence)
   - Python backend source module.

2. Requirement Served
   - Supports secure, cost-controlled API delivery for OwenWrites backend features.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - Broad exception handling present at lines: 71.
   - Recommendation: narrow exception scopes, remove `any`, and enforce typed interfaces.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "except Exception|print\(" backend/config/demo_config.py`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: backend/database/migrations/001_cost_optimization_tables_fixed.sql

1. Purpose Summary (1 sentence)
   - Defines database schema migrations and operational SQL routines.

2. Requirement Served
   - Supports secure, cost-controlled API delivery for OwenWrites backend features.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: backend/database/migrations/002_guest_sessions.sql

1. Purpose Summary (1 sentence)
   - Defines database schema migrations and operational SQL routines.

2. Requirement Served
   - Supports secure, cost-controlled API delivery for OwenWrites backend features.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: backend/dependencies.py

1. Purpose Summary (1 sentence)
   - Python backend source module.

2. Requirement Served
   - Supports secure, cost-controlled API delivery for OwenWrites backend features.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - Broad exception handling present at lines: 79, 149, 196.
   - Recommendation: narrow exception scopes, remove `any`, and enforce typed interfaces.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "except Exception|print\(" backend/dependencies.py`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: backend/main.py

1. Purpose Summary (1 sentence)
   - Python backend source module.

2. Requirement Served
   - Supports secure, cost-controlled API delivery for OwenWrites backend features.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - Debug `print(...)` calls at lines: 105, 112.
   - Contains commented-out grammar router registration (stale configuration).
   - Flag for deletion: Yes (safe after behavior check).
   - Rationale: reduces noise and maintenance surface.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - Broad exception handling present at lines: 38, 70, 80, 88, 163, 182, 261, 297, 318, 329, 347, 379.
   - `logging.basicConfig` found at line(s): 12; should be app-bootstrap only.
   - Recommendation: narrow exception scopes, remove `any`, and enforce typed interfaces.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "except Exception|print\(" backend/main.py`

12. Priority & Risk
    - Priority: P1
    - Risk of change: Med

Additional Verified Findings:
- Complexity / Readability: Startup file manages env checks, dynamic imports, router binding, middleware, and admin endpoints in one module. (lines: 1)
- Action: Move startup checks to dedicated bootstrap module and keep `main.py` thin.
- Dead Code / Unreachable / Unused: Commented grammar router line is stale/dead configuration. (lines: 47)
- Action: Remove dead route comment and keep route matrix in one source.

---

FILE: backend/middleware/security_middleware.py

1. Purpose Summary (1 sentence)
   - Applies cross-cutting security and request-processing controls.

2. Requirement Served
   - Supports secure, cost-controlled API delivery for OwenWrites backend features.

3. Redundancy Found
   - Duplicated client-IP extraction logic overlaps these files: `backend/utils/request_helpers.py`, `backend/services/rate_limiter.py`, `backend/middleware/security_middleware.py`.
   - Recommendation: abstract shared behavior into one module and import it.
   - Proposed refactor snippet: `from utils.request_helpers import get_client_ip` or `import { tokenStore } from "./tokenStore"`

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - Broad exception handling present at lines: 167.
   - Recommendation: narrow exception scopes, remove `any`, and enforce typed interfaces.

7. Security Risks
   - CSP contains weak directives (`unsafe-inline`/`unsafe-eval`) at lines: 74, 75.
   - Fix recommendation: centralize secure error handling/CSP/token policy and fail-closed for costly endpoints.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "except Exception|print\(" backend/middleware/security_middleware.py`

12. Priority & Risk
    - Priority: P1
    - Risk of change: Med

Additional Verified Findings:
- Security Risks: CSP includes `script-src "unsafe-inline"`. (lines: 74)
- Action: Use nonce-based scripts or strict script whitelist to reduce XSS risk.
- Redundancy Found: Own IP extraction duplicates helper in `backend/utils/request_helpers.py`. (lines: 177)
- Action: Reuse shared helper to avoid divergence.

---

FILE: backend/models/__init__.py

1. Purpose Summary (1 sentence)
   - Defines shared data contracts and validation schemas.

2. Requirement Served
   - Supports secure, cost-controlled API delivery for OwenWrites backend features.

3. Redundancy Found
   - Implementation pattern is similar to `backend/services/__init__.py`; avoid diverging duplicated styles/exports.
   - Recommendation: abstract shared behavior into one module and import it.
   - Proposed refactor snippet: `from utils.request_helpers import get_client_ip` or `import { tokenStore } from "./tokenStore"`

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Mostly stylistic/structural sibling of `backend/services/__init__.py`; keep conventions aligned.
   - Simplification suggestions: move side-effect code to dedicated helpers and keep public surface minimal.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "except Exception|print\(" backend/models/__init__.py`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: backend/models/schemas.py

1. Purpose Summary (1 sentence)
   - Defines shared data contracts and validation schemas.

2. Requirement Served
   - Supports secure, cost-controlled API delivery for OwenWrites backend features.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "except Exception|print\(" backend/models/schemas.py`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: backend/nixpacks.toml

1. Purpose Summary (1 sentence)
   - Project/deploy/tooling configuration.

2. Requirement Served
   - Supports secure, cost-controlled API delivery for OwenWrites backend features.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: backend/requirements.txt

1. Purpose Summary (1 sentence)
   - Pinned Python dependency manifest for backend runtime.

2. Requirement Served
   - Supports secure, cost-controlled API delivery for OwenWrites backend features.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: backend/routers/__init__.py

1. Purpose Summary (1 sentence)
   - Defines HTTP endpoints and request/response orchestration for a domain.

2. Requirement Served
   - Supports secure, cost-controlled API delivery for OwenWrites backend features.

3. Redundancy Found
   - Implementation pattern is similar to `backend/services/__init__.py`; avoid diverging duplicated styles/exports.
   - Recommendation: abstract shared behavior into one module and import it.
   - Proposed refactor snippet: `from utils.request_helpers import get_client_ip` or `import { tokenStore } from "./tokenStore"`

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - Standardize router error responses via `backend/utils/error_responses.py`.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Mostly stylistic/structural sibling of `backend/services/__init__.py`; keep conventions aligned.
   - Simplification suggestions: move side-effect code to dedicated helpers and keep public surface minimal.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Missing edge-case tests for this file’s key behaviors and error paths.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "except Exception|print\(" backend/routers/__init__.py`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: backend/routers/auth_router.py

1. Purpose Summary (1 sentence)
   - Defines HTTP endpoints and request/response orchestration for a domain.

2. Requirement Served
   - Supports secure, cost-controlled API delivery for OwenWrites backend features.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - Standardize router error responses via `backend/utils/error_responses.py`.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - Broad exception handling present at lines: 93, 140, 172, 194, 257, 307, 341, 410, 417.
   - Recommendation: narrow exception scopes, remove `any`, and enforce typed interfaces.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - File length is high (423 lines).
   - Simplification suggestions: move side-effect code to dedicated helpers and keep public surface minimal.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Missing edge-case tests for this file’s key behaviors and error paths.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "except Exception|print\(" backend/routers/auth_router.py`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: backend/routers/character_voice_router.py

1. Purpose Summary (1 sentence)
   - Defines HTTP endpoints and request/response orchestration for a domain.

2. Requirement Served
   - Supports secure, cost-controlled API delivery for OwenWrites backend features.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - Standardize router error responses via `backend/utils/error_responses.py`.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - Broad exception handling present at lines: 103, 179, 207, 260, 300, 340, 372.
   - Recommendation: narrow exception scopes, remove `any`, and enforce typed interfaces.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Missing edge-case tests for this file’s key behaviors and error paths.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "except Exception|print\(" backend/routers/character_voice_router.py`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: backend/routers/chat_router.py

1. Purpose Summary (1 sentence)
   - Defines HTTP endpoints and request/response orchestration for a domain.

2. Requirement Served
   - Supports secure, cost-controlled API delivery for OwenWrites backend features.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - Standardize router error responses via `backend/utils/error_responses.py`.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - Broad exception handling present at lines: 444, 496, 526, 603, 761, 788, 801.
   - Recommendation: narrow exception scopes, remove `any`, and enforce typed interfaces.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - Large file size (810 lines) raises cognitive and runtime branching overhead.
   - Severity: Med
   - Fix suggestion: split responsibilities and reduce high-frequency state churn.

9. Complexity / Readability
   - File length is high (810 lines).
   - Acts as multi-responsibility “god module”; split by domain concern.
   - Simplification suggestions: move side-effect code to dedicated helpers and keep public surface minimal.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Missing edge-case tests for this file’s key behaviors and error paths.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "except Exception|print\(" backend/routers/chat_router.py`

12. Priority & Risk
    - Priority: P1
    - Risk of change: Med

Additional Verified Findings:
- Complexity / Readability: Large endpoint mixes validation, prompt building, cache analytics, voice analysis, and response parsing. (lines: 110)
- Action: Split into orchestrator + pure helpers (`validate`, `assemble`, `parse`, `augment`).

---

FILE: backend/routers/cost_optimization_router.py

1. Purpose Summary (1 sentence)
   - Defines HTTP endpoints and request/response orchestration for a domain.

2. Requirement Served
   - Supports secure, cost-controlled API delivery for OwenWrites backend features.

3. Redundancy Found
   - Uses ad-hoc `HTTPException` payloads while other routers use standardized `error_response` helper.
   - Recommendation: abstract shared behavior into one module and import it.
   - Proposed refactor snippet: `from utils.request_helpers import get_client_ip` or `import { tokenStore } from "./tokenStore"`

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - Standardize router error responses via `backend/utils/error_responses.py`.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - Broad exception handling present at lines: 98, 155, 195, 218.
   - Recommendation: narrow exception scopes, remove `any`, and enforce typed interfaces.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Missing edge-case tests for this file’s key behaviors and error paths.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "except Exception|print\(" backend/routers/cost_optimization_router.py`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: backend/routers/document_router.py

1. Purpose Summary (1 sentence)
   - Defines HTTP endpoints and request/response orchestration for a domain.

2. Requirement Served
   - Supports secure, cost-controlled API delivery for OwenWrites backend features.

3. Redundancy Found
   - Uses ad-hoc `HTTPException` payloads while other routers use standardized `error_response` helper.
   - Recommendation: abstract shared behavior into one module and import it.
   - Proposed refactor snippet: `from utils.request_helpers import get_client_ip` or `import { tokenStore } from "./tokenStore"`

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - Standardize router error responses via `backend/utils/error_responses.py`.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Missing edge-case tests for this file’s key behaviors and error paths.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "except Exception|print\(" backend/routers/document_router.py`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: backend/routers/folder_router.py

1. Purpose Summary (1 sentence)
   - Defines HTTP endpoints and request/response orchestration for a domain.

2. Requirement Served
   - Supports secure, cost-controlled API delivery for OwenWrites backend features.

3. Redundancy Found
   - Uses ad-hoc `HTTPException` payloads while other routers use standardized `error_response` helper.
   - Recommendation: abstract shared behavior into one module and import it.
   - Proposed refactor snippet: `from utils.request_helpers import get_client_ip` or `import { tokenStore } from "./tokenStore"`

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - Standardize router error responses via `backend/utils/error_responses.py`.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Missing edge-case tests for this file’s key behaviors and error paths.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "except Exception|print\(" backend/routers/folder_router.py`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: backend/routers/grammar_router.py

1. Purpose Summary (1 sentence)
   - Defines HTTP endpoints and request/response orchestration for a domain.

2. Requirement Served
   - Supports secure, cost-controlled API delivery for OwenWrites backend features.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - Standardize router error responses via `backend/utils/error_responses.py`.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - Broad exception handling present at lines: 115, 155.
   - Recommendation: narrow exception scopes, remove `any`, and enforce typed interfaces.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Missing edge-case tests for this file’s key behaviors and error paths.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "except Exception|print\(" backend/routers/grammar_router.py`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: backend/routers/indexing_router.py

1. Purpose Summary (1 sentence)
   - Defines HTTP endpoints and request/response orchestration for a domain.

2. Requirement Served
   - Supports secure, cost-controlled API delivery for OwenWrites backend features.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - Standardize router error responses via `backend/utils/error_responses.py`.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - Broad exception handling present at lines: 77, 106, 126, 146, 165, 194, 214, 233.
   - Recommendation: narrow exception scopes, remove `any`, and enforce typed interfaces.

7. Security Risks
   - Leaks internal exception text to clients at lines: 78, 107, 127, 147, 166, 195, 215, 234.
   - Fix recommendation: centralize secure error handling/CSP/token policy and fail-closed for costly endpoints.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Missing edge-case tests for this file’s key behaviors and error paths.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "except Exception|print\(" backend/routers/indexing_router.py`

12. Priority & Risk
    - Priority: P1
    - Risk of change: Med

Additional Verified Findings:
- Redundancy Found: Repeated `except Exception` handlers leak raw internals via `detail=str(e)`. (lines: 78, 107, 127, 147, 166, 195, 215, 234)
- Action: Switch to `error_response()` and log internal exception details server-side only.
- Security Risks: Raw exception details are returned to clients. (lines: 78, 107, 127, 147, 166, 195, 215, 234)
- Action: Return stable `code/message` payloads; keep traceback in logs only.

---

FILE: backend/routers/local_ai_router.py

1. Purpose Summary (1 sentence)
   - Defines HTTP endpoints and request/response orchestration for a domain.

2. Requirement Served
   - Supports secure, cost-controlled API delivery for OwenWrites backend features.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - Standardize router error responses via `backend/utils/error_responses.py`.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - Broad exception handling present at lines: 47, 72, 119, 181, 349.
   - Recommendation: narrow exception scopes, remove `any`, and enforce typed interfaces.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Missing edge-case tests for this file’s key behaviors and error paths.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "except Exception|print\(" backend/routers/local_ai_router.py`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: backend/routers/story_generator_router.py

1. Purpose Summary (1 sentence)
   - Defines HTTP endpoints and request/response orchestration for a domain.

2. Requirement Served
   - Supports secure, cost-controlled API delivery for OwenWrites backend features.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - Standardize router error responses via `backend/utils/error_responses.py`.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - Broad exception handling present at lines: 133.
   - Recommendation: narrow exception scopes, remove `any`, and enforce typed interfaces.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Missing edge-case tests for this file’s key behaviors and error paths.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "except Exception|print\(" backend/routers/story_generator_router.py`

12. Priority & Risk
    - Priority: P1
    - Risk of change: Med

Additional Verified Findings:
- Security Risks: Builds a very large prompt with raw interpolated user inputs. (lines: 85)
- Action: Add prompt sanitization and bounded formatting; separate system/user templates.

---

FILE: backend/runtime.txt

1. Purpose Summary (1 sentence)
   - Repository source/configuration artifact.

2. Requirement Served
   - Supports secure, cost-controlled API delivery for OwenWrites backend features.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: backend/services/__init__.py

1. Purpose Summary (1 sentence)
   - Implements backend domain logic, integrations, or infrastructure concerns.

2. Requirement Served
   - Supports secure, cost-controlled API delivery for OwenWrites backend features.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Missing edge-case tests for this file’s key behaviors and error paths.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "except Exception|print\(" backend/services/__init__.py`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: backend/services/auth_service.py

1. Purpose Summary (1 sentence)
   - Implements backend domain logic, integrations, or infrastructure concerns.

2. Requirement Served
   - Supports secure, cost-controlled API delivery for OwenWrites backend features.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - Debug `print(...)` calls at lines: 34, 40, 48.
   - Open TODO/FIXME markers at lines: 830.
   - Flag for deletion: Yes (safe after behavior check).
   - Rationale: reduces noise and maintenance surface.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - Broad exception handling present at lines: 194, 271, 323, 391, 452, 463, 500, 590, 656, 675, 701, 739, ....
   - Recommendation: narrow exception scopes, remove `any`, and enforce typed interfaces.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - Large file size (856 lines) raises cognitive and runtime branching overhead.
   - Severity: Med
   - Fix suggestion: split responsibilities and reduce high-frequency state churn.

9. Complexity / Readability
   - File length is high (856 lines).
   - Acts as multi-responsibility “god module”; split by domain concern.
   - Simplification suggestions: move side-effect code to dedicated helpers and keep public surface minimal.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Missing edge-case tests for this file’s key behaviors and error paths.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "except Exception|print\(" backend/services/auth_service.py`

12. Priority & Risk
    - Priority: P1
    - Risk of change: Med

Additional Verified Findings:
- Dead Code / Unreachable / Unused: Guest conversion calls `_migrate_guest_data`, but body is TODO/no-op. (lines: 830)
- Action: Either implement migration or remove conversion path until ready.
- Complexity / Readability: Service contains registration/login/JWT/guest session/analytics/conversion in one class. (lines: 1)
- Action: Split auth core from guest-session and analytics services.

---

FILE: backend/services/character_voice_service.py

1. Purpose Summary (1 sentence)
   - Implements backend domain logic, integrations, or infrastructure concerns.

2. Requirement Served
   - Supports secure, cost-controlled API delivery for OwenWrites backend features.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - Broad exception handling present at lines: 128, 419, 653, 873.
   - `logging.basicConfig` found at line(s): 27; should be app-bootstrap only.
   - Recommendation: narrow exception scopes, remove `any`, and enforce typed interfaces.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - Large file size (885 lines) raises cognitive and runtime branching overhead.
   - Severity: Med
   - Fix suggestion: split responsibilities and reduce high-frequency state churn.

9. Complexity / Readability
   - File length is high (885 lines).
   - Acts as multi-responsibility “god module”; split by domain concern.
   - Simplification suggestions: move side-effect code to dedicated helpers and keep public surface minimal.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Missing edge-case tests for this file’s key behaviors and error paths.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "except Exception|print\(" backend/services/character_voice_service.py`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

Additional Verified Findings:
- Type Safety / Best Practices Issues: `logging.basicConfig(...)` executed at module import. (lines: 27)
- Action: Configure logging centrally in app bootstrap only.

---

FILE: backend/services/database.py

1. Purpose Summary (1 sentence)
   - Implements backend domain logic, integrations, or infrastructure concerns.

2. Requirement Served
   - Supports secure, cost-controlled API delivery for OwenWrites backend features.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - Debug `print(...)` calls at lines: 186, 187, 191, 205, 209, 215, 218, 219, 221, 223, 225, 227, ....
   - Flag for deletion: Yes (safe after behavior check).
   - Rationale: reduces noise and maintenance surface.

5. Abstraction Opportunities
   - Extract DB core, schema migration, and feature repositories into separate modules.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - Broad exception handling present at lines: 45, 94, 129, 172, 443, 451, 460, 470, 479, 501, 523, 537, ....
   - Recommendation: narrow exception scopes, remove `any`, and enforce typed interfaces.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - Large file size (819 lines) raises cognitive and runtime branching overhead.
   - Heavy runtime console printing inside query path can slow request throughput.
   - Severity: High
   - Fix suggestion: split responsibilities and reduce high-frequency state churn.

9. Complexity / Readability
   - File length is high (819 lines).
   - Acts as multi-responsibility “god module”; split by domain concern.
   - Simplification suggestions: move side-effect code to dedicated helpers and keep public surface minimal.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Missing edge-case tests for this file’s key behaviors and error paths.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "except Exception|print\(" backend/services/database.py`

12. Priority & Risk
    - Priority: P1
    - Risk of change: Med

Additional Verified Findings:
- Dead Code / Unreachable / Unused: Production-path `print(...)` debug statements remain in `execute_query`. (lines: 186, 187, 191, 205, 209, 215, 218, 219, 221, 223, 225, 227, ...)
- Action: Replace with structured logger at `debug` level or remove.
- Complexity / Readability: Single class combines pool lifecycle, schema migration, CRUD helpers, and feature-specific profile logic. (lines: 1)
- Action: Split into `db_core.py`, `db_schema.py`, and domain repositories.

---

FILE: backend/services/dialogue_extractor.py

1. Purpose Summary (1 sentence)
   - Implements backend domain logic, integrations, or infrastructure concerns.

2. Requirement Served
   - Supports secure, cost-controlled API delivery for OwenWrites backend features.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Missing edge-case tests for this file’s key behaviors and error paths.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "except Exception|print\(" backend/services/dialogue_extractor.py`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: backend/services/enhanced_validation.py

1. Purpose Summary (1 sentence)
   - Implements backend domain logic, integrations, or infrastructure concerns.

2. Requirement Served
   - Supports secure, cost-controlled API delivery for OwenWrites backend features.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Missing edge-case tests for this file’s key behaviors and error paths.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "except Exception|print\(" backend/services/enhanced_validation.py`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: backend/services/grammar_service.py

1. Purpose Summary (1 sentence)
   - Implements backend domain logic, integrations, or infrastructure concerns.

2. Requirement Served
   - Supports secure, cost-controlled API delivery for OwenWrites backend features.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - Broad exception handling present at lines: 320, 455, 540.
   - Calls method `generate_response_async` without matching service definition in backend services.
   - Recommendation: narrow exception scopes, remove `any`, and enforce typed interfaces.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - File length is high (586 lines).
   - Simplification suggestions: move side-effect code to dedicated helpers and keep public surface minimal.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Missing edge-case tests for this file’s key behaviors and error paths.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "except Exception|print\(" backend/services/grammar_service.py`

12. Priority & Risk
    - Priority: P1
    - Risk of change: Med

Additional Verified Findings:
- Type Safety / Best Practices Issues: Calls `llm_service.generate_response_async(...)`, but this symbol is not defined elsewhere in services. (lines: 445)
- Action: Use existing async LLM API method or add typed adapter in `llm_service.py`.

---

FILE: backend/services/indexing/__init__.py

1. Purpose Summary (1 sentence)
   - Implements backend domain logic, integrations, or infrastructure concerns.

2. Requirement Served
   - Supports secure, cost-controlled API delivery for OwenWrites backend features.

3. Redundancy Found
   - Implementation pattern is similar to `backend/services/__init__.py`; avoid diverging duplicated styles/exports.
   - Recommendation: abstract shared behavior into one module and import it.
   - Proposed refactor snippet: `from utils.request_helpers import get_client_ip` or `import { tokenStore } from "./tokenStore"`

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Mostly stylistic/structural sibling of `backend/services/__init__.py`; keep conventions aligned.
   - Simplification suggestions: move side-effect code to dedicated helpers and keep public surface minimal.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Missing edge-case tests for this file’s key behaviors and error paths.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "except Exception|print\(" backend/services/indexing/__init__.py`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: backend/services/indexing/graph_builder.py

1. Purpose Summary (1 sentence)
   - Implements backend domain logic, integrations, or infrastructure concerns.

2. Requirement Served
   - Supports secure, cost-controlled API delivery for OwenWrites backend features.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - Broad exception handling present at lines: 146, 340.
   - Recommendation: narrow exception scopes, remove `any`, and enforce typed interfaces.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Missing edge-case tests for this file’s key behaviors and error paths.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "except Exception|print\(" backend/services/indexing/graph_builder.py`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: backend/services/indexing/hybrid_indexer.py

1. Purpose Summary (1 sentence)
   - Implements backend domain logic, integrations, or infrastructure concerns.

2. Requirement Served
   - Supports secure, cost-controlled API delivery for OwenWrites backend features.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - Broad exception handling present at lines: 175, 260, 268, 276, 285, 325, 338, 558, 848, 886, 942, 997, ....
   - Recommendation: narrow exception scopes, remove `any`, and enforce typed interfaces.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - Large file size (1360 lines) raises cognitive and runtime branching overhead.
   - Severity: Med
   - Fix suggestion: split responsibilities and reduce high-frequency state churn.

9. Complexity / Readability
   - File length is high (1360 lines).
   - Simplification suggestions: move side-effect code to dedicated helpers and keep public surface minimal.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Missing edge-case tests for this file’s key behaviors and error paths.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "except Exception|print\(" backend/services/indexing/hybrid_indexer.py`

12. Priority & Risk
    - Priority: P2
    - Risk of change: Med

---

FILE: backend/services/indexing/path_retriever.py

1. Purpose Summary (1 sentence)
   - Implements backend domain logic, integrations, or infrastructure concerns.

2. Requirement Served
   - Supports secure, cost-controlled API delivery for OwenWrites backend features.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - File length is high (438 lines).
   - Simplification suggestions: move side-effect code to dedicated helpers and keep public surface minimal.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Missing edge-case tests for this file’s key behaviors and error paths.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "except Exception|print\(" backend/services/indexing/path_retriever.py`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: backend/services/indexing/vector_store.py

1. Purpose Summary (1 sentence)
   - Implements backend domain logic, integrations, or infrastructure concerns.

2. Requirement Served
   - Supports secure, cost-controlled API delivery for OwenWrites backend features.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - Debug `print(...)` calls at lines: 45, 49.
   - Flag for deletion: Yes (safe after behavior check).
   - Rationale: reduces noise and maintenance surface.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - Broad exception handling present at lines: 48.
   - Recommendation: narrow exception scopes, remove `any`, and enforce typed interfaces.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Missing edge-case tests for this file’s key behaviors and error paths.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "except Exception|print\(" backend/services/indexing/vector_store.py`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

Additional Verified Findings:
- Dead Code / Unreachable / Unused: Uses `print` for runtime diagnostics. (lines: 45, 49)
- Action: Replace with module logger and severity levels.

---

FILE: backend/services/infra_service.py

1. Purpose Summary (1 sentence)
   - Implements backend domain logic, integrations, or infrastructure concerns.

2. Requirement Served
   - Supports secure, cost-controlled API delivery for OwenWrites backend features.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - Open TODO/FIXME markers at lines: 181.
   - Flag for deletion: Yes (safe after behavior check).
   - Rationale: reduces noise and maintenance surface.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - Broad exception handling present at lines: 143, 195, 289, 334, 385, 437, 469, 524.
   - Recommendation: narrow exception scopes, remove `any`, and enforce typed interfaces.

7. Security Risks
   - Fail-open behavior on rate-limiter errors can increase spend and abuse risk.
   - Fix recommendation: centralize secure error handling/CSP/token policy and fail-closed for costly endpoints.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - File length is high (534 lines).
   - Simplification suggestions: move side-effect code to dedicated helpers and keep public surface minimal.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Missing edge-case tests for this file’s key behaviors and error paths.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "except Exception|print\(" backend/services/infra_service.py`

12. Priority & Risk
    - Priority: P1
    - Risk of change: Med

Additional Verified Findings:
- Security Risks: Rate limiter fails open on backend errors in `check_limit`. (lines: 131)
- Action: Fail closed for expensive endpoints; keep explicit fail-open only for low-cost routes.

---

FILE: backend/services/llm/__init__.py

1. Purpose Summary (1 sentence)
   - Implements backend domain logic, integrations, or infrastructure concerns.

2. Requirement Served
   - Supports secure, cost-controlled API delivery for OwenWrites backend features.

3. Redundancy Found
   - Implementation pattern is similar to `backend/services/__init__.py`; avoid diverging duplicated styles/exports.
   - Recommendation: abstract shared behavior into one module and import it.
   - Proposed refactor snippet: `from utils.request_helpers import get_client_ip` or `import { tokenStore } from "./tokenStore"`

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - `logging.basicConfig` found at line(s): 12; should be app-bootstrap only.
   - Recommendation: narrow exception scopes, remove `any`, and enforce typed interfaces.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Mostly stylistic/structural sibling of `backend/services/__init__.py`; keep conventions aligned.
   - Simplification suggestions: move side-effect code to dedicated helpers and keep public surface minimal.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Missing edge-case tests for this file’s key behaviors and error paths.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "except Exception|print\(" backend/services/llm/__init__.py`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: backend/services/llm/base_service.py

1. Purpose Summary (1 sentence)
   - Implements backend domain logic, integrations, or infrastructure concerns.

2. Requirement Served
   - Supports secure, cost-controlled API delivery for OwenWrites backend features.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Missing edge-case tests for this file’s key behaviors and error paths.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "except Exception|print\(" backend/services/llm/base_service.py`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: backend/services/llm/gemini_service.py

1. Purpose Summary (1 sentence)
   - Implements backend domain logic, integrations, or infrastructure concerns.

2. Requirement Served
   - Supports secure, cost-controlled API delivery for OwenWrites backend features.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - Broad exception handling present at lines: 30, 56, 123, 199, 203, 243, 275, 341.
   - Recommendation: narrow exception scopes, remove `any`, and enforce typed interfaces.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Missing edge-case tests for this file’s key behaviors and error paths.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "except Exception|print\(" backend/services/llm/gemini_service.py`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: backend/services/llm/huggingface_service.py

1. Purpose Summary (1 sentence)
   - Implements backend domain logic, integrations, or infrastructure concerns.

2. Requirement Served
   - Supports secure, cost-controlled API delivery for OwenWrites backend features.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - Broad exception handling present at lines: 247, 313, 379.
   - Recommendation: narrow exception scopes, remove `any`, and enforce typed interfaces.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - File length is high (470 lines).
   - Simplification suggestions: move side-effect code to dedicated helpers and keep public surface minimal.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Missing edge-case tests for this file’s key behaviors and error paths.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "except Exception|print\(" backend/services/llm/huggingface_service.py`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: backend/services/llm/hybrid_service.py

1. Purpose Summary (1 sentence)
   - Implements backend domain logic, integrations, or infrastructure concerns.

2. Requirement Served
   - Supports secure, cost-controlled API delivery for OwenWrites backend features.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - Broad exception handling present at lines: 31, 169, 224.
   - Recommendation: narrow exception scopes, remove `any`, and enforce typed interfaces.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - File length is high (492 lines).
   - Simplification suggestions: move side-effect code to dedicated helpers and keep public surface minimal.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Missing edge-case tests for this file’s key behaviors and error paths.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "except Exception|print\(" backend/services/llm/hybrid_service.py`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: backend/services/llm/ollama_service.py

1. Purpose Summary (1 sentence)
   - Implements backend domain logic, integrations, or infrastructure concerns.

2. Requirement Served
   - Supports secure, cost-controlled API delivery for OwenWrites backend features.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - Broad exception handling present at lines: 114, 206.
   - Recommendation: narrow exception scopes, remove `any`, and enforce typed interfaces.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Missing edge-case tests for this file’s key behaviors and error paths.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "except Exception|print\(" backend/services/llm/ollama_service.py`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: backend/services/llm/openai_service.py

1. Purpose Summary (1 sentence)
   - Implements backend domain logic, integrations, or infrastructure concerns.

2. Requirement Served
   - Supports secure, cost-controlled API delivery for OwenWrites backend features.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - Broad exception handling present at lines: 72, 128.
   - Recommendation: narrow exception scopes, remove `any`, and enforce typed interfaces.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Missing edge-case tests for this file’s key behaviors and error paths.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "except Exception|print\(" backend/services/llm/openai_service.py`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: backend/services/llm_service.py

1. Purpose Summary (1 sentence)
   - Implements backend domain logic, integrations, or infrastructure concerns.

2. Requirement Served
   - Supports secure, cost-controlled API delivery for OwenWrites backend features.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - Broad exception handling present at lines: 34, 45, 56, 67, 78, 224, 465, 521, 595.
   - Recommendation: narrow exception scopes, remove `any`, and enforce typed interfaces.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - Large file size (630 lines) raises cognitive and runtime branching overhead.
   - Severity: Med
   - Fix suggestion: split responsibilities and reduce high-frequency state churn.

9. Complexity / Readability
   - File length is high (630 lines).
   - Simplification suggestions: move side-effect code to dedicated helpers and keep public surface minimal.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Missing edge-case tests for this file’s key behaviors and error paths.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "except Exception|print\(" backend/services/llm_service.py`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: backend/services/rate_limiter.py

1. Purpose Summary (1 sentence)
   - Implements backend domain logic, integrations, or infrastructure concerns.

2. Requirement Served
   - Supports secure, cost-controlled API delivery for OwenWrites backend features.

3. Redundancy Found
   - Duplicated client-IP extraction logic overlaps these files: `backend/utils/request_helpers.py`, `backend/services/rate_limiter.py`, `backend/middleware/security_middleware.py`.
   - Recommendation: abstract shared behavior into one module and import it.
   - Proposed refactor snippet: `from utils.request_helpers import get_client_ip` or `import { tokenStore } from "./tokenStore"`

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Missing edge-case tests for this file’s key behaviors and error paths.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "except Exception|print\(" backend/services/rate_limiter.py`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

Additional Verified Findings:
- Redundancy Found: Defines `get_client_ip` wrapper while shared helper already exists. (lines: 34)
- Action: Inline `extract_client_ip(request)` directly or centralize in dependency layer.

---

FILE: backend/services/security_logger.py

1. Purpose Summary (1 sentence)
   - Implements backend domain logic, integrations, or infrastructure concerns.

2. Requirement Served
   - Supports secure, cost-controlled API delivery for OwenWrites backend features.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - Broad exception handling present at lines: 91.
   - Recommendation: narrow exception scopes, remove `any`, and enforce typed interfaces.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Missing edge-case tests for this file’s key behaviors and error paths.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "except Exception|print\(" backend/services/security_logger.py`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: backend/services/validation_service.py

1. Purpose Summary (1 sentence)
   - Implements backend domain logic, integrations, or infrastructure concerns.

2. Requirement Served
   - Supports secure, cost-controlled API delivery for OwenWrites backend features.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - Broad exception handling present at lines: 260.
   - Recommendation: narrow exception scopes, remove `any`, and enforce typed interfaces.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Missing edge-case tests for this file’s key behaviors and error paths.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "except Exception|print\(" backend/services/validation_service.py`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: backend/start.sh

1. Purpose Summary (1 sentence)
   - Deployment or runtime shell automation script.

2. Requirement Served
   - Supports secure, cost-controlled API delivery for OwenWrites backend features.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: backend/utils/error_responses.py

1. Purpose Summary (1 sentence)
   - Provides reusable helper utilities shared across modules.

2. Requirement Served
   - Supports secure, cost-controlled API delivery for OwenWrites backend features.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "except Exception|print\(" backend/utils/error_responses.py`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: backend/utils/helpers.py

1. Purpose Summary (1 sentence)
   - Provides reusable helper utilities shared across modules.

2. Requirement Served
   - Supports secure, cost-controlled API delivery for OwenWrites backend features.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "except Exception|print\(" backend/utils/helpers.py`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: backend/utils/request_helpers.py

1. Purpose Summary (1 sentence)
   - Provides reusable helper utilities shared across modules.

2. Requirement Served
   - Supports secure, cost-controlled API delivery for OwenWrites backend features.

3. Redundancy Found
   - Duplicated client-IP extraction logic overlaps these files: `backend/utils/request_helpers.py`, `backend/services/rate_limiter.py`, `backend/middleware/security_middleware.py`.
   - Recommendation: abstract shared behavior into one module and import it.
   - Proposed refactor snippet: `from utils.request_helpers import get_client_ip` or `import { tokenStore } from "./tokenStore"`

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "except Exception|print\(" backend/utils/request_helpers.py`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/.gitignore

1. Purpose Summary (1 sentence)
   - Repository source/configuration artifact.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/.npmrc

1. Purpose Summary (1 sentence)
   - Repository source/configuration artifact.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/.nvmrc

1. Purpose Summary (1 sentence)
   - Repository source/configuration artifact.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/eslint.config.js

1. Purpose Summary (1 sentence)
   - Repository source/configuration artifact.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/index.html

1. Purpose Summary (1 sentence)
   - Repository source/configuration artifact.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/package-lock.json

1. Purpose Summary (1 sentence)
   - Lockfile pinning npm dependency graph for reproducible installs.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - Large file size (5916 lines) raises cognitive and runtime branching overhead.
   - Severity: Med
   - Fix suggestion: split responsibilities and reduce high-frequency state churn.

9. Complexity / Readability
   - File length is high (5916 lines).
   - Simplification suggestions: move side-effect code to dedicated helpers and keep public surface minimal.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).

12. Priority & Risk
    - Priority: P2
    - Risk of change: Low

---

FILE: frontend/package.json

1. Purpose Summary (1 sentence)
   - Structured configuration/data resource used by app/tooling.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/railway-build.sh

1. Purpose Summary (1 sentence)
   - Deployment or runtime shell automation script.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/App.css

1. Purpose Summary (1 sentence)
   - Contains presentation and layout styles for frontend UI.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - Large file size (894 lines) raises cognitive and runtime branching overhead.
   - Severity: Med
   - Fix suggestion: split responsibilities and reduce high-frequency state churn.

9. Complexity / Readability
   - File length is high (894 lines).
   - Simplification suggestions: move side-effect code to dedicated helpers and keep public surface minimal.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/App.tsx

1. Purpose Summary (1 sentence)
   - TypeScript React implementation file.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - Uses `dangerouslySetInnerHTML` at lines: 57.
   - Fix recommendation: centralize secure error handling/CSP/token policy and fail-closed for costly endpoints.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/App.tsx`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

Additional Verified Findings:
- Security Risks: Uses `<style dangerouslySetInnerHTML=...>` for runtime CSS injection. (lines: 57)
- Action: Move style tokens to static CSS/variables and avoid runtime HTML injection API.

---

FILE: frontend/src/components/AuthModal.tsx

1. Purpose Summary (1 sentence)
   - Renders UI and interactions for a specific frontend feature.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - Hook dependency drift flagged at L25
   - Recommendation: narrow exception scopes, remove `any`, and enforce typed interfaces.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/components/AuthModal.tsx`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/components/ChatPane.tsx

1. Purpose Summary (1 sentence)
   - Renders UI and interactions for a specific frontend feature.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/components/ChatPane.tsx`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/components/DocumentHelp.tsx

1. Purpose Summary (1 sentence)
   - Renders UI and interactions for a specific frontend feature.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/components/DocumentHelp.tsx`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/components/DocumentManager.css

1. Purpose Summary (1 sentence)
   - Renders UI and interactions for a specific frontend feature.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - Large file size (2052 lines) raises cognitive and runtime branching overhead.
   - Severity: Med
   - Fix suggestion: split responsibilities and reduce high-frequency state churn.

9. Complexity / Readability
   - File length is high (2052 lines).
   - Simplification suggestions: move side-effect code to dedicated helpers and keep public surface minimal.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/components/DocumentManager.tsx

1. Purpose Summary (1 sentence)
   - Renders UI and interactions for a specific frontend feature.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/components/DocumentManager.tsx`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/components/DocumentTitleBar.tsx

1. Purpose Summary (1 sentence)
   - Renders UI and interactions for a specific frontend feature.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/components/DocumentTitleBar.tsx`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/components/ErrorBoundary.tsx

1. Purpose Summary (1 sentence)
   - Renders UI and interactions for a specific frontend feature.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - Open TODO/FIXME markers at lines: 49.
   - Flag for deletion: Yes (safe after behavior check).
   - Rationale: reduces noise and maintenance surface.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/components/ErrorBoundary.tsx`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/components/HighlightableEditor.tsx

1. Purpose Summary (1 sentence)
   - Renders UI and interactions for a specific frontend feature.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - Large file size (814 lines) raises cognitive and runtime branching overhead.
   - Severity: Med
   - Fix suggestion: split responsibilities and reduce high-frequency state churn.

9. Complexity / Readability
   - File length is high (814 lines).
   - Simplification suggestions: move side-effect code to dedicated helpers and keep public surface minimal.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/components/HighlightableEditor.tsx`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/components/StoryGeneratorModal.tsx

1. Purpose Summary (1 sentence)
   - Renders UI and interactions for a specific frontend feature.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - Large file size (704 lines) raises cognitive and runtime branching overhead.
   - Severity: Med
   - Fix suggestion: split responsibilities and reduce high-frequency state churn.

9. Complexity / Readability
   - File length is high (704 lines).
   - Simplification suggestions: move side-effect code to dedicated helpers and keep public surface minimal.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/components/StoryGeneratorModal.tsx`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/components/UserProfileModal.tsx

1. Purpose Summary (1 sentence)
   - Renders UI and interactions for a specific frontend feature.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - File length is high (470 lines).
   - Simplification suggestions: move side-effect code to dedicated helpers and keep public surface minimal.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/components/UserProfileModal.tsx`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/components/WritingWorkspace.tsx

1. Purpose Summary (1 sentence)
   - Renders UI and interactions for a specific frontend feature.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - File length is high (411 lines).
   - Simplification suggestions: move side-effect code to dedicated helpers and keep public surface minimal.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/components/WritingWorkspace.tsx`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/components/auth/AuthForm.tsx

1. Purpose Summary (1 sentence)
   - Renders UI and interactions for a specific frontend feature.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/components/auth/AuthForm.tsx`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/components/auth/FormField.tsx

1. Purpose Summary (1 sentence)
   - Renders UI and interactions for a specific frontend feature.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/components/auth/FormField.tsx`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/components/auth/ModalContainer.tsx

1. Purpose Summary (1 sentence)
   - Renders UI and interactions for a specific frontend feature.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/components/auth/ModalContainer.tsx`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/components/auth/PasswordInput.tsx

1. Purpose Summary (1 sentence)
   - Renders UI and interactions for a specific frontend feature.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/components/auth/PasswordInput.tsx`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/components/auth/index.ts

1. Purpose Summary (1 sentence)
   - Renders UI and interactions for a specific frontend feature.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/components/auth/index.ts`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/components/auth/useAuthFormValidation.ts

1. Purpose Summary (1 sentence)
   - Renders UI and interactions for a specific frontend feature.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - Hook dependency drift flagged at L30
   - Recommendation: narrow exception scopes, remove `any`, and enforce typed interfaces.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/components/auth/useAuthFormValidation.ts`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/components/chat-interface/ChatHeader.tsx

1. Purpose Summary (1 sentence)
   - Renders UI and interactions for a specific frontend feature.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/components/chat-interface/ChatHeader.tsx`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/components/chat-interface/EnhancedChatInput.tsx

1. Purpose Summary (1 sentence)
   - Renders UI and interactions for a specific frontend feature.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - Unused symbol findings from ESLint: L23, L24, L25, L34, L34
   - Flag for deletion: Yes (safe after behavior check).
   - Rationale: reduces noise and maintenance surface.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/components/chat-interface/EnhancedChatInput.tsx`

12. Priority & Risk
    - Priority: P2
    - Risk of change: Med

---

FILE: frontend/src/components/chat-interface/EnhancedChatMessage.tsx

1. Purpose Summary (1 sentence)
   - Renders UI and interactions for a specific frontend feature.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/components/chat-interface/EnhancedChatMessage.tsx`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/components/chat-interface/ErrorDisplay.tsx

1. Purpose Summary (1 sentence)
   - Renders UI and interactions for a specific frontend feature.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/components/chat-interface/ErrorDisplay.tsx`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/components/chat-interface/HighlightedTextDisplay.tsx

1. Purpose Summary (1 sentence)
   - Renders UI and interactions for a specific frontend feature.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/components/chat-interface/HighlightedTextDisplay.tsx`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/components/chat-interface/MessagesContainer.tsx

1. Purpose Summary (1 sentence)
   - Renders UI and interactions for a specific frontend feature.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/components/chat-interface/MessagesContainer.tsx`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/components/chat-interface/PromptTemplates.ts

1. Purpose Summary (1 sentence)
   - Renders UI and interactions for a specific frontend feature.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/components/chat-interface/PromptTemplates.ts`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/components/chat-interface/SuggestionsDisplay.css

1. Purpose Summary (1 sentence)
   - Renders UI and interactions for a specific frontend feature.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - File length is high (416 lines).
   - Simplification suggestions: move side-effect code to dedicated helpers and keep public surface minimal.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/components/chat-interface/SuggestionsDisplay.tsx

1. Purpose Summary (1 sentence)
   - Renders UI and interactions for a specific frontend feature.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - Unused symbol findings from ESLint: L77
   - Flag for deletion: Yes (safe after behavior check).
   - Rationale: reduces noise and maintenance surface.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/components/chat-interface/SuggestionsDisplay.tsx`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/components/chat-interface/UnhighlightButton.tsx

1. Purpose Summary (1 sentence)
   - Renders UI and interactions for a specific frontend feature.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/components/chat-interface/UnhighlightButton.tsx`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/components/chat-interface/index.ts

1. Purpose Summary (1 sentence)
   - Renders UI and interactions for a specific frontend feature.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - Implementation pattern is similar to `frontend/src/services/api/index.ts`; avoid diverging duplicated styles/exports.
   - Recommendation: abstract shared behavior into one module and import it.
   - Proposed refactor snippet: `from utils.request_helpers import get_client_ip` or `import { tokenStore } from "./tokenStore"`

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Mostly stylistic/structural sibling of `frontend/src/services/api/index.ts`; keep conventions aligned.
   - Simplification suggestions: move side-effect code to dedicated helpers and keep public surface minimal.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/components/chat-interface/index.ts`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/components/chat/ThinkingTrail.tsx

1. Purpose Summary (1 sentence)
   - Renders UI and interactions for a specific frontend feature.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/components/chat/ThinkingTrail.tsx`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/components/document-manager/AppMapView.tsx

1. Purpose Summary (1 sentence)
   - Renders UI and interactions for a specific frontend feature.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/components/document-manager/AppMapView.tsx`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/components/document-manager/AuthPrompt.tsx

1. Purpose Summary (1 sentence)
   - Renders UI and interactions for a specific frontend feature.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/components/document-manager/AuthPrompt.tsx`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/components/document-manager/CreateModal.tsx

1. Purpose Summary (1 sentence)
   - Renders UI and interactions for a specific frontend feature.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/components/document-manager/CreateModal.tsx`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/components/document-manager/DocumentIcon.tsx

1. Purpose Summary (1 sentence)
   - Renders UI and interactions for a specific frontend feature.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/components/document-manager/DocumentIcon.tsx`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/components/document-manager/DocumentItem.tsx

1. Purpose Summary (1 sentence)
   - Renders UI and interactions for a specific frontend feature.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/components/document-manager/DocumentItem.tsx`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/components/document-manager/DocumentManagerHeader.tsx

1. Purpose Summary (1 sentence)
   - Renders UI and interactions for a specific frontend feature.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/components/document-manager/DocumentManagerHeader.tsx`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/components/document-manager/DocumentsView.tsx

1. Purpose Summary (1 sentence)
   - Renders UI and interactions for a specific frontend feature.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - Unused symbol findings from ESLint: L19
   - Flag for deletion: Yes (safe after behavior check).
   - Rationale: reduces noise and maintenance surface.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/components/document-manager/DocumentsView.tsx`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/components/document-manager/FolderItem.tsx

1. Purpose Summary (1 sentence)
   - Renders UI and interactions for a specific frontend feature.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/components/document-manager/FolderItem.tsx`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/components/document-manager/FoldersView.tsx

1. Purpose Summary (1 sentence)
   - Renders UI and interactions for a specific frontend feature.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/components/document-manager/FoldersView.tsx`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/components/document-manager/NavigationTabs.tsx

1. Purpose Summary (1 sentence)
   - Renders UI and interactions for a specific frontend feature.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/components/document-manager/NavigationTabs.tsx`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/components/document-manager/SearchBar.tsx

1. Purpose Summary (1 sentence)
   - Renders UI and interactions for a specific frontend feature.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/components/document-manager/SearchBar.tsx`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/components/document-manager/SearchResultsView.tsx

1. Purpose Summary (1 sentence)
   - Renders UI and interactions for a specific frontend feature.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/components/document-manager/SearchResultsView.tsx`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/components/document-manager/index.ts

1. Purpose Summary (1 sentence)
   - Renders UI and interactions for a specific frontend feature.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - Implementation pattern is similar to `frontend/src/components/document-manager/types.ts`; avoid diverging duplicated styles/exports.
   - Recommendation: abstract shared behavior into one module and import it.
   - Proposed refactor snippet: `from utils.request_helpers import get_client_ip` or `import { tokenStore } from "./tokenStore"`

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Mostly stylistic/structural sibling of `frontend/src/components/document-manager/types.ts`; keep conventions aligned.
   - Simplification suggestions: move side-effect code to dedicated helpers and keep public surface minimal.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/components/document-manager/index.ts`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/components/document-manager/types.ts

1. Purpose Summary (1 sentence)
   - Renders UI and interactions for a specific frontend feature.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/components/document-manager/types.ts`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/components/editor-layout/EditorPanel.tsx

1. Purpose Summary (1 sentence)
   - Renders UI and interactions for a specific frontend feature.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/components/editor-layout/EditorPanel.tsx`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/components/editor-layout/TextSelectionHandler.tsx

1. Purpose Summary (1 sentence)
   - Renders UI and interactions for a specific frontend feature.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/components/editor-layout/TextSelectionHandler.tsx`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/constants/documentThemes.ts

1. Purpose Summary (1 sentence)
   - TypeScript source or configuration module.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - File length is high (464 lines).
   - Simplification suggestions: move side-effect code to dedicated helpers and keep public surface minimal.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/constants/documentThemes.ts`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/contexts/AppContext.tsx

1. Purpose Summary (1 sentence)
   - Provides React context state and behavior across component trees.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/contexts/AppContext.tsx`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/contexts/AuthContext.tsx

1. Purpose Summary (1 sentence)
   - Provides React context state and behavior across component trees.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - Token lifecycle logic duplicated across auth context and API layer (`set/get/remove` localStorage + refresh handling).
   - Recommendation: abstract shared behavior into one module and import it.
   - Proposed refactor snippet: `from utils.request_helpers import get_client_ip` or `import { tokenStore } from "./tokenStore"`

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - Split auth token plumbing from view state into `useAuthSession` + provider.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - `any` type usage flagged by ESLint at L205, L206, L207, L255, L425, L426, L427, L428, L429, L430, ...
   - Hook dependency drift flagged at L191, L214, L347, L388
   - Recommendation: narrow exception scopes, remove `any`, and enforce typed interfaces.

7. Security Risks
   - Direct token storage in `localStorage` appears in this file; increases XSS blast radius.
   - Fix recommendation: centralize secure error handling/CSP/token policy and fail-closed for costly endpoints.

8. Performance Issues
   - Large file size (672 lines) raises cognitive and runtime branching overhead.
   - Severity: Med
   - Fix suggestion: split responsibilities and reduce high-frequency state churn.

9. Complexity / Readability
   - File length is high (672 lines).
   - Acts as multi-responsibility “god module”; split by domain concern.
   - Simplification suggestions: move side-effect code to dedicated helpers and keep public surface minimal.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/contexts/AuthContext.tsx`

12. Priority & Risk
    - Priority: P1
    - Risk of change: Med

Additional Verified Findings:
- Redundancy Found: Auth token storage/refresh logic duplicates `services/api/auth.ts` and `services/api/client.ts`. (lines: 116, 138, 157, 367)
- Action: Centralize token lifecycle in one auth-token module and consume from context/client.
- Dead Code / Unreachable / Unused: ESLint reports 23 errors (mostly `any` + stale vars). (lines: 205, 255, 425, 491, 536, 619)
- Action: Eliminate `any`, remove unused variables, and tighten types for error objects.

---

FILE: frontend/src/contexts/ChatContext.tsx

1. Purpose Summary (1 sentence)
   - Provides React context state and behavior across component trees.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - Unused symbol findings from ESLint: L123, L128, L136
   - Flag for deletion: Yes (safe after behavior check).
   - Rationale: reduces noise and maintenance surface.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - `any` type usage flagged by ESLint at L92, L120, L136, L575
   - Hook dependency drift flagged at L301
   - Recommendation: narrow exception scopes, remove `any`, and enforce typed interfaces.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - Large file size (767 lines) raises cognitive and runtime branching overhead.
   - High-frequency custom events and broad context updates can re-render many consumers.
   - Severity: Med
   - Fix suggestion: split responsibilities and reduce high-frequency state churn.

9. Complexity / Readability
   - File length is high (767 lines).
   - Acts as multi-responsibility “god module”; split by domain concern.
   - Simplification suggestions: move side-effect code to dedicated helpers and keep public surface minimal.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/contexts/ChatContext.tsx`

12. Priority & Risk
    - Priority: P1
    - Risk of change: Med

Additional Verified Findings:
- Dead Code / Unreachable / Unused: Unused cache helpers (`getCacheKey`, `checkCache`, `setCache`) and `any` types flagged by ESLint. (lines: 123, 128, 136)
- Action: Delete unused cache block or wire it properly with typed API layer.
- Complexity / Readability: Context orchestrates chat + suggestions + highlighting + onboarding + premium flags in one provider. (lines: 1)
- Action: Split into smaller contexts or compose with dedicated hooks.

---

FILE: frontend/src/contexts/DocumentThemeContext.tsx

1. Purpose Summary (1 sentence)
   - Provides React context state and behavior across component trees.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/contexts/DocumentThemeContext.tsx`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/contexts/EditorContext.tsx

1. Purpose Summary (1 sentence)
   - Provides React context state and behavior across component trees.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/contexts/EditorContext.tsx`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/contexts/ThemeContext.tsx

1. Purpose Summary (1 sentence)
   - Provides React context state and behavior across component trees.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/contexts/ThemeContext.tsx`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/contexts/UIContext.tsx

1. Purpose Summary (1 sentence)
   - Provides React context state and behavior across component trees.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - Mirrors auth-derived fields (`user`, `isAuthenticated`) already available from `AuthContext`.
   - Recommendation: abstract shared behavior into one module and import it.
   - Proposed refactor snippet: `from utils.request_helpers import get_client_ip` or `import { tokenStore } from "./tokenStore"`

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - `any` type usage flagged by ESLint at L7
   - Recommendation: narrow exception scopes, remove `any`, and enforce typed interfaces.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/contexts/UIContext.tsx`

12. Priority & Risk
    - Priority: P1
    - Risk of change: Med

Additional Verified Findings:
- Redundancy Found: Context duplicates auth-derived state and only adds modal state. (lines: 7)
- Action: Fold modal state into `AuthContext` and remove `UIContext` layer.

---

FILE: frontend/src/extensions/HighlightDecorations.ts

1. Purpose Summary (1 sentence)
   - TypeScript source or configuration module.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - `any` type usage flagged by ESLint at L150, L194, L205, L219, L223
   - Recommendation: narrow exception scopes, remove `any`, and enforce typed interfaces.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/extensions/HighlightDecorations.ts`

12. Priority & Risk
    - Priority: P1
    - Risk of change: Med

Additional Verified Findings:
- Type Safety / Best Practices Issues: ESLint errors for `no-case-declarations` and multiple `any` signatures. (lines: 68, 70, 150, 194, 205, 219, 223)
- Action: Fix switch scoping and strongly type command contexts.

---

FILE: frontend/src/extensions/VoiceInconsistencyMark.ts

1. Purpose Summary (1 sentence)
   - TypeScript source or configuration module.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - `any` type usage flagged by ESLint at L4
   - Recommendation: narrow exception scopes, remove `any`, and enforce typed interfaces.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/extensions/VoiceInconsistencyMark.ts`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/hooks/useApiHealth.ts

1. Purpose Summary (1 sentence)
   - Encapsulates reusable React state/effects for app features.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Missing edge-case tests for this file’s key behaviors and error paths.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/hooks/useApiHealth.ts`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/hooks/useChat.ts

1. Purpose Summary (1 sentence)
   - Encapsulates reusable React state/effects for app features.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - Unused symbol findings from ESLint: L2, L2, L3, L4, L5, L5, L85, L300
   - Flag for deletion: Yes (safe after behavior check).
   - Rationale: reduces noise and maintenance surface.

5. Abstraction Opportunities
   - Split streaming, transport, and fallback-error flows into smaller hooks.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - Hook dependency drift flagged at L131, L477
   - Recommendation: narrow exception scopes, remove `any`, and enforce typed interfaces.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - Interval-based placeholder updates can trigger extra renders during streaming.
   - Severity: Med
   - Fix suggestion: split responsibilities and reduce high-frequency state churn.

9. Complexity / Readability
   - File length is high (516 lines).
   - Acts as multi-responsibility “god module”; split by domain concern.
   - Simplification suggestions: move side-effect code to dedicated helpers and keep public surface minimal.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Missing edge-case tests for this file’s key behaviors and error paths.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/hooks/useChat.ts`

12. Priority & Risk
    - Priority: P1
    - Risk of change: Med

Additional Verified Findings:
- Dead Code / Unreachable / Unused: ESLint flags multiple unused imports/vars and missing deps in hooks. (lines: 2, 85, 131, 300, 477)
- Action: Prune unused code paths and stabilize hook dependencies.
- Complexity / Readability: Single hook handles transport, stream simulation, fallback UX, events, and analytics. (lines: 1)
- Action: Split into `useChatTransport`, `useChatStreaming`, `useChatErrors`.

---

FILE: frontend/src/hooks/useDocuments.ts

1. Purpose Summary (1 sentence)
   - Encapsulates reusable React state/effects for app features.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - Hook dependency drift flagged at L280
   - Recommendation: narrow exception scopes, remove `any`, and enforce typed interfaces.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - Large file size (659 lines) raises cognitive and runtime branching overhead.
   - Severity: Med
   - Fix suggestion: split responsibilities and reduce high-frequency state churn.

9. Complexity / Readability
   - File length is high (659 lines).
   - Acts as multi-responsibility “god module”; split by domain concern.
   - Simplification suggestions: move side-effect code to dedicated helpers and keep public surface minimal.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Missing edge-case tests for this file’s key behaviors and error paths.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/hooks/useDocuments.ts`

12. Priority & Risk
    - Priority: P1
    - Risk of change: Med

Additional Verified Findings:
- Complexity / Readability: High state surface with auto-save, dedupe, retry, CRUD, folder ops, and search in one hook. (lines: 1)
- Action: Split into `useDocumentCrud`, `useAutoSave`, `useDocumentSearch`.

---

FILE: frontend/src/hooks/useEditor.ts

1. Purpose Summary (1 sentence)
   - Encapsulates reusable React state/effects for app features.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Missing edge-case tests for this file’s key behaviors and error paths.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/hooks/useEditor.ts`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/hooks/useSafeState.ts

1. Purpose Summary (1 sentence)
   - Encapsulates reusable React state/effects for app features.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Missing edge-case tests for this file’s key behaviors and error paths.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/hooks/useSafeState.ts`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/index.css

1. Purpose Summary (1 sentence)
   - Contains presentation and layout styles for frontend UI.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/main.tsx

1. Purpose Summary (1 sentence)
   - TypeScript React implementation file.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/main.tsx`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/pages/DocumentEditor.css

1. Purpose Summary (1 sentence)
   - Composes route-level UI pages from lower-level components.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/pages/DocumentEditor.tsx

1. Purpose Summary (1 sentence)
   - Composes route-level UI pages from lower-level components.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - Hook dependency drift flagged at L74, L82, L90
   - Recommendation: narrow exception scopes, remove `any`, and enforce typed interfaces.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/pages/DocumentEditor.tsx`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/pages/DocumentsPage.css

1. Purpose Summary (1 sentence)
   - Composes route-level UI pages from lower-level components.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - Large file size (678 lines) raises cognitive and runtime branching overhead.
   - Severity: Med
   - Fix suggestion: split responsibilities and reduce high-frequency state churn.

9. Complexity / Readability
   - File length is high (678 lines).
   - Simplification suggestions: move side-effect code to dedicated helpers and keep public surface minimal.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/pages/DocumentsPage.tsx

1. Purpose Summary (1 sentence)
   - Composes route-level UI pages from lower-level components.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - Unused symbol findings from ESLint: L11, L100
   - Flag for deletion: Yes (safe after behavior check).
   - Rationale: reduces noise and maintenance surface.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - `any` type usage flagged by ESLint at L182
   - Recommendation: narrow exception scopes, remove `any`, and enforce typed interfaces.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/pages/DocumentsPage.tsx`

12. Priority & Risk
    - Priority: P1
    - Risk of change: Med

Additional Verified Findings:
- Dead Code / Unreachable / Unused: References `getRecentDocuments` from `useDocuments`, but hook does not export it. (lines: 24, 100)
- Action: Add function to hook or remove usage.
- Type Safety / Best Practices Issues: Contains `any` cast in sort handler. (lines: 182)
- Action: Use explicit union type cast without `any`.

---

FILE: frontend/src/services/api.ts

1. Purpose Summary (1 sentence)
   - Implements backend domain logic, integrations, or infrastructure concerns.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/services/api.ts`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/services/api/auth.ts

1. Purpose Summary (1 sentence)
   - Implements backend domain logic, integrations, or infrastructure concerns.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - Token lifecycle logic duplicated across auth context and API layer (`set/get/remove` localStorage + refresh handling).
   - Recommendation: abstract shared behavior into one module and import it.
   - Proposed refactor snippet: `from utils.request_helpers import get_client_ip` or `import { tokenStore } from "./tokenStore"`

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - Use one shared token store + interceptor policy for all API modules.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - Direct token storage in `localStorage` appears in this file; increases XSS blast radius.
   - Fix recommendation: centralize secure error handling/CSP/token policy and fail-closed for costly endpoints.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Missing edge-case tests for this file’s key behaviors and error paths.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/services/api/auth.ts`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

Additional Verified Findings:
- Redundancy Found: Token localStorage operations are duplicated in two other modules. (lines: 51, 72, 82)
- Action: Delegate to shared `tokenStore` and keep this file API-only.

---

FILE: frontend/src/services/api/character-voice.ts

1. Purpose Summary (1 sentence)
   - Implements backend domain logic, integrations, or infrastructure concerns.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - Use one shared token store + interceptor policy for all API modules.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - `any` type usage flagged by ESLint at L38, L208
   - Recommendation: narrow exception scopes, remove `any`, and enforce typed interfaces.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Missing edge-case tests for this file’s key behaviors and error paths.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/services/api/character-voice.ts`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/services/api/chat.ts

1. Purpose Summary (1 sentence)
   - Implements backend domain logic, integrations, or infrastructure concerns.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - Token lifecycle logic duplicated across auth context and API layer (`set/get/remove` localStorage + refresh handling).
   - Recommendation: abstract shared behavior into one module and import it.
   - Proposed refactor snippet: `from utils.request_helpers import get_client_ip` or `import { tokenStore } from "./tokenStore"`

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - Use one shared token store + interceptor policy for all API modules.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - `any` type usage flagged by ESLint at L78, L123, L128, L140, L142
   - Recommendation: narrow exception scopes, remove `any`, and enforce typed interfaces.

7. Security Risks
   - Direct token storage in `localStorage` appears in this file; increases XSS blast radius.
   - Fix recommendation: centralize secure error handling/CSP/token policy and fail-closed for costly endpoints.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Missing edge-case tests for this file’s key behaviors and error paths.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/services/api/chat.ts`

12. Priority & Risk
    - Priority: P2
    - Risk of change: Med

Additional Verified Findings:
- Type Safety / Best Practices Issues: Public API signatures use `any`. (lines: 78, 123, 128, 140, 142)
- Action: Introduce strict request/response types from `types.ts`.

---

FILE: frontend/src/services/api/client.ts

1. Purpose Summary (1 sentence)
   - Implements backend domain logic, integrations, or infrastructure concerns.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - Token lifecycle logic duplicated across auth context and API layer (`set/get/remove` localStorage + refresh handling).
   - Recommendation: abstract shared behavior into one module and import it.
   - Proposed refactor snippet: `from utils.request_helpers import get_client_ip` or `import { tokenStore } from "./tokenStore"`

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - Use one shared token store + interceptor policy for all API modules.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - Direct token storage in `localStorage` appears in this file; increases XSS blast radius.
   - Fix recommendation: centralize secure error handling/CSP/token policy and fail-closed for costly endpoints.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Missing edge-case tests for this file’s key behaviors and error paths.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/services/api/client.ts`

12. Priority & Risk
    - Priority: P1
    - Risk of change: Med

Additional Verified Findings:
- Redundancy Found: Performs token persistence/cleanup already present in `AuthContext` and `api/auth.ts`. (lines: 99, 124, 285)
- Action: Create single token store utility used by both client and context.
- Complexity / Readability: Contains two response interceptors with overlapping concerns. (lines: 174, 194)
- Action: Merge into one deterministic interceptor pipeline.

---

FILE: frontend/src/services/api/documents.ts

1. Purpose Summary (1 sentence)
   - Implements backend domain logic, integrations, or infrastructure concerns.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - Use one shared token store + interceptor policy for all API modules.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - `any` type usage flagged by ESLint at L55
   - Recommendation: narrow exception scopes, remove `any`, and enforce typed interfaces.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Missing edge-case tests for this file’s key behaviors and error paths.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/services/api/documents.ts`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/services/api/folders.ts

1. Purpose Summary (1 sentence)
   - Implements backend domain logic, integrations, or infrastructure concerns.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - Use one shared token store + interceptor policy for all API modules.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Missing edge-case tests for this file’s key behaviors and error paths.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/services/api/folders.ts`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/services/api/index.ts

1. Purpose Summary (1 sentence)
   - Implements backend domain logic, integrations, or infrastructure concerns.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - Use one shared token store + interceptor policy for all API modules.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - `any` type usage flagged by ESLint at L89
   - Recommendation: narrow exception scopes, remove `any`, and enforce typed interfaces.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Missing edge-case tests for this file’s key behaviors and error paths.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/services/api/index.ts`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/services/api/search.ts

1. Purpose Summary (1 sentence)
   - Implements backend domain logic, integrations, or infrastructure concerns.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - Use one shared token store + interceptor policy for all API modules.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Missing edge-case tests for this file’s key behaviors and error paths.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/services/api/search.ts`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/services/api/types.ts

1. Purpose Summary (1 sentence)
   - Implements backend domain logic, integrations, or infrastructure concerns.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - Use one shared token store + interceptor policy for all API modules.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - `any` type usage flagged by ESLint at L18, L71, L98
   - Recommendation: narrow exception scopes, remove `any`, and enforce typed interfaces.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Missing edge-case tests for this file’s key behaviors and error paths.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/services/api/types.ts`

12. Priority & Risk
    - Priority: P1
    - Risk of change: Med

Additional Verified Findings:
- Type Safety / Best Practices Issues: Core shared types still use `any`. (lines: 18, 71, 98)
- Action: Replace with domain-specific interfaces (`WritingStyleProfile`, `PositionInfo`, etc.).

---

FILE: frontend/src/styles/auth.css

1. Purpose Summary (1 sentence)
   - Contains presentation and layout styles for frontend UI.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - Implementation pattern is similar to `frontend/src/styles/components.css`; avoid diverging duplicated styles/exports.
   - Recommendation: abstract shared behavior into one module and import it.
   - Proposed refactor snippet: `from utils.request_helpers import get_client_ip` or `import { tokenStore } from "./tokenStore"`

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - Large file size (712 lines) raises cognitive and runtime branching overhead.
   - Severity: Med
   - Fix suggestion: split responsibilities and reduce high-frequency state churn.

9. Complexity / Readability
   - File length is high (712 lines).
   - Mostly stylistic/structural sibling of `frontend/src/styles/components.css`; keep conventions aligned.
   - Simplification suggestions: move side-effect code to dedicated helpers and keep public surface minimal.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/styles/components.css

1. Purpose Summary (1 sentence)
   - Contains presentation and layout styles for frontend UI.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - Implementation pattern is similar to `frontend/src/styles/editor.css`; avoid diverging duplicated styles/exports.
   - Recommendation: abstract shared behavior into one module and import it.
   - Proposed refactor snippet: `from utils.request_helpers import get_client_ip` or `import { tokenStore } from "./tokenStore"`

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - Large file size (2982 lines) raises cognitive and runtime branching overhead.
   - Severity: Med
   - Fix suggestion: split responsibilities and reduce high-frequency state churn.

9. Complexity / Readability
   - File length is high (2982 lines).
   - Mostly stylistic/structural sibling of `frontend/src/styles/editor.css`; keep conventions aligned.
   - Simplification suggestions: move side-effect code to dedicated helpers and keep public surface minimal.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/styles/design-system.css

1. Purpose Summary (1 sentence)
   - Contains presentation and layout styles for frontend UI.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - Implementation pattern is similar to `frontend/src/styles/components.css`; avoid diverging duplicated styles/exports.
   - Recommendation: abstract shared behavior into one module and import it.
   - Proposed refactor snippet: `from utils.request_helpers import get_client_ip` or `import { tokenStore } from "./tokenStore"`

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - Large file size (621 lines) raises cognitive and runtime branching overhead.
   - Severity: Med
   - Fix suggestion: split responsibilities and reduce high-frequency state churn.

9. Complexity / Readability
   - File length is high (621 lines).
   - Mostly stylistic/structural sibling of `frontend/src/styles/components.css`; keep conventions aligned.
   - Simplification suggestions: move side-effect code to dedicated helpers and keep public surface minimal.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/styles/editor-panel.css

1. Purpose Summary (1 sentence)
   - Contains presentation and layout styles for frontend UI.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/styles/editor.css

1. Purpose Summary (1 sentence)
   - Contains presentation and layout styles for frontend UI.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - Large file size (1004 lines) raises cognitive and runtime branching overhead.
   - Severity: Med
   - Fix suggestion: split responsibilities and reduce high-frequency state churn.

9. Complexity / Readability
   - File length is high (1004 lines).
   - Simplification suggestions: move side-effect code to dedicated helpers and keep public surface minimal.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/styles/enhanced-ui.css

1. Purpose Summary (1 sentence)
   - Contains presentation and layout styles for frontend UI.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - Implementation pattern is similar to `frontend/src/styles/components.css`; avoid diverging duplicated styles/exports.
   - Recommendation: abstract shared behavior into one module and import it.
   - Proposed refactor snippet: `from utils.request_helpers import get_client_ip` or `import { tokenStore } from "./tokenStore"`

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Mostly stylistic/structural sibling of `frontend/src/styles/components.css`; keep conventions aligned.
   - Simplification suggestions: move side-effect code to dedicated helpers and keep public surface minimal.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/styles/global.css

1. Purpose Summary (1 sentence)
   - Contains presentation and layout styles for frontend UI.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/styles/highlightable-editor.css

1. Purpose Summary (1 sentence)
   - Contains presentation and layout styles for frontend UI.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - Implementation pattern is similar to `frontend/src/styles/editor.css`; avoid diverging duplicated styles/exports.
   - Recommendation: abstract shared behavior into one module and import it.
   - Proposed refactor snippet: `from utils.request_helpers import get_client_ip` or `import { tokenStore } from "./tokenStore"`

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - Large file size (759 lines) raises cognitive and runtime branching overhead.
   - Severity: Med
   - Fix suggestion: split responsibilities and reduce high-frequency state churn.

9. Complexity / Readability
   - File length is high (759 lines).
   - Mostly stylistic/structural sibling of `frontend/src/styles/editor.css`; keep conventions aligned.
   - Simplification suggestions: move side-effect code to dedicated helpers and keep public surface minimal.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/styles/suggestions-compact-fix.css

1. Purpose Summary (1 sentence)
   - Contains presentation and layout styles for frontend UI.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - Implementation pattern is similar to `frontend/src/styles/components.css`; avoid diverging duplicated styles/exports.
   - Recommendation: abstract shared behavior into one module and import it.
   - Proposed refactor snippet: `from utils.request_helpers import get_client_ip` or `import { tokenStore } from "./tokenStore"`

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Mostly stylistic/structural sibling of `frontend/src/styles/components.css`; keep conventions aligned.
   - Simplification suggestions: move side-effect code to dedicated helpers and keep public surface minimal.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/styles/text-selection.css

1. Purpose Summary (1 sentence)
   - Contains presentation and layout styles for frontend UI.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/styles/voice-consistency-underlines.css

1. Purpose Summary (1 sentence)
   - Contains presentation and layout styles for frontend UI.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - Implementation pattern is similar to `frontend/src/styles/components.css`; avoid diverging duplicated styles/exports.
   - Recommendation: abstract shared behavior into one module and import it.
   - Proposed refactor snippet: `from utils.request_helpers import get_client_ip` or `import { tokenStore } from "./tokenStore"`

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Mostly stylistic/structural sibling of `frontend/src/styles/components.css`; keep conventions aligned.
   - Simplification suggestions: move side-effect code to dedicated helpers and keep public surface minimal.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/utils/logger.ts

1. Purpose Summary (1 sentence)
   - Provides reusable helper utilities shared across modules.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/utils/logger.ts`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/src/vite-env.d.ts

1. Purpose Summary (1 sentence)
   - TypeScript source or configuration module.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/src/vite-env.d.ts`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/tsconfig.app.json

1. Purpose Summary (1 sentence)
   - Structured configuration/data resource used by app/tooling.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/tsconfig.json

1. Purpose Summary (1 sentence)
   - Structured configuration/data resource used by app/tooling.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/tsconfig.node.json

1. Purpose Summary (1 sentence)
   - Structured configuration/data resource used by app/tooling.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: frontend/vite.config.ts

1. Purpose Summary (1 sentence)
   - TypeScript source or configuration module.

2. Requirement Served
   - Supports writer-facing SPA UX, state, and API integration for OwenWrites.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).
    - `rg -n "any|localStorage|console\.(log|error)" frontend/vite.config.ts`

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---

FILE: railway.toml

1. Purpose Summary (1 sentence)
   - Project/deploy/tooling configuration.

2. Requirement Served
   - Supports repository governance, tooling, or deployment reproducibility.

3. Redundancy Found
   - No strong duplication signal from static scan for this file.
   - Recommendation: keep as-is in this pass.
   - Proposed refactor snippet: N/A

4. Dead Code / Unreachable / Unused
   - No dead/unreachable indicators from this pass.
   - Flag for deletion: No.
   - Rationale: active code path or config artifact.

5. Abstraction Opportunities
   - No mandatory abstraction in this pass.
   - Example refactor: create `shared/tokenStore.ts` and replace direct `localStorage` calls.

6. Type Safety / Best Practices Issues
   - No major type-safety finding from this pass.
   - Recommendation: keep strict typing baseline and avoid regressions.

7. Security Risks
   - No immediate security-critical issue detected for this file in this pass.

8. Performance Issues
   - No major performance bottleneck identified for this file.
   - Severity: Low
   - Fix suggestion: N/A

9. Complexity / Readability
   - Readability is acceptable for current scope.
   - Simplification suggestions: optional.

10. Test Coverage Gaps
    - No automated tests discovered (`pytest` reports no tests, frontend has no `npm test` script).
    - Low-risk file; direct tests optional unless behavior changes.

11. Suggested Commands for Reproduction
    - `cd backend && pytest -q --maxfail=1` (currently: no tests found).
    - `cd frontend && npx eslint . --ext .ts,.tsx` (currently: errors/warnings in targeted TS files).
    - `cd frontend && npx tsc --noEmit` (currently passes in this environment).

12. Priority & Risk
    - Priority: P3
    - Risk of change: Low

---
