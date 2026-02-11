# Consolidation Plan

## Proposed Shared Modules
- `backend/utils/request_helpers.py` as the sole client-IP parser.
- `backend/utils/error_responses.py` as the sole structured error payload builder.
- `frontend/src/services/auth/tokenStore.ts` for all token get/set/clear/expiry logic.
- `frontend/src/services/api/interceptors.ts` for one response interceptor pipeline.
- `frontend/src/hooks/chat/` split: `useChatTransport.ts`, `useChatStreaming.ts`, `useChatErrors.ts`.
- `frontend/src/hooks/documents/` split: `useDocumentCrud.ts`, `useAutoSave.ts`, `useDocumentSearch.ts`.

## Suggested Target Structure
```text
backend/
  utils/
    error_responses.py
    request_helpers.py
  services/
    auth/
      auth_service.py
      guest_service.py
    db/
      db_core.py
      db_schema.py
      repositories/
frontend/src/
  services/
    auth/tokenStore.ts
    api/interceptors.ts
  hooks/
    chat/useChatTransport.ts
    chat/useChatStreaming.ts
    chat/useChatErrors.ts
    documents/useDocumentCrud.ts
    documents/useAutoSave.ts
    documents/useDocumentSearch.ts
```