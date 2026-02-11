# Deletion Candidate List

These are high-confidence removals or trims that do not require behavior changes.

- `backend/services/database.py`: remove debug `print(...)` calls in `execute_query` (L186-L244 pattern).
- `backend/main.py`: remove stale commented grammar-router line (L47).
- `frontend/src/contexts/ChatContext.tsx`: remove unused cache helpers `getCacheKey`, `checkCache`, `setCache` (L123, L128, L136).
- `frontend/src/components/chat-interface/EnhancedChatInput.tsx`: remove unused context variables (`handleSendMessage`, `isThinking`, `isStreaming`, `isExpanded`, `setIsExpanded`).
- `frontend/src/pages/DocumentsPage.tsx`: remove `user` and `recentDocuments` locals if not used.
- `frontend/src/contexts/UIContext.tsx`: candidate for full removal after moving modal state to `AuthContext`.
- `backend/services/auth_service.py`: remove or defer `convert_guest_to_user` migration path until `_migrate_guest_data` is implemented.

Low-confidence (defer until verified):
- Any router/endpoint removal not currently called by frontend.
- Style/doc/config files that may be used by deployment/tooling.