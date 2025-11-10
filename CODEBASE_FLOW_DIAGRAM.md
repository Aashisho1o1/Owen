# Complete Request Flow: Story Generator

## Visual Journey from Click to Response

```
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 1: USER CLICKS "GENERATE STORY"                                │
│ File: frontend/src/components/StoryGeneratorModal.tsx:463          │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 2: FRONTEND - Check Authentication                             │
│ File: frontend/src/components/StoryGeneratorModal.tsx:120          │
│                                                                      │
│ Code:                                                                │
│   let token = localStorage.getItem('owen_access_token');           │
│   if (!token) {                                                     │
│     await createGuestSession();  // ← Create guest if no token     │
│   }                                                                 │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 3: FRONTEND - Make HTTP Request                                │
│ File: frontend/src/contexts/AuthContext.tsx:577                    │
│                                                                      │
│ Request:                                                             │
│   POST https://backend.../api/auth/guest                           │
│   Headers: {                                                        │
│     "Content-Type": "application/json"                             │
│   }                                                                 │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 4: BACKEND - Router Receives Request                           │
│ File: backend/routers/auth_router.py:189                           │
│                                                                      │
│ Code:                                                                │
│   @router.post("/guest")                                            │
│   async def create_guest_session(request: Request):                │
│       await check_rate_limit(request, "auth")  // ← Check limits  │
│       result = auth_service.create_guest_session(...)             │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 5: BACKEND - Service Creates Session                           │
│ File: backend/services/auth_service.py:540                         │
│                                                                      │
│ Code:                                                                │
│   def create_guest_session(self, ip_address, user_agent):         │
│       self._ensure_guest_table_exists()  // ← THE FIX!            │
│       session_id = str(uuid.uuid4())                               │
│       guest_token = jwt.encode(payload, SECRET)                    │
│       self.db.execute_query("INSERT INTO guest_sessions...")       │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 6: DATABASE - Store Guest Session                              │
│ Database: PostgreSQL on Railway                                     │
│                                                                      │
│ Query:                                                               │
│   INSERT INTO guest_sessions (                                      │
│     id, session_token, ip_address, expires_at                      │
│   ) VALUES (                                                        │
│     'abc-123', 'jwt_xyz...', '192.168.1.5', '2025-11-11'          │
│   )                                                                 │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 7: BACKEND - Return Token                                      │
│ File: backend/services/auth_service.py:568                         │
│                                                                      │
│ Response:                                                            │
│   {                                                                  │
│     "access_token": "eyJhbGc...",  ← JWT token                     │
│     "token_type": "bearer",                                         │
│     "expires_in": 86400,           ← 24 hours                      │
│     "user": {                                                       │
│       "id": "guest_abc123",                                         │
│       "username": "Guest abc123",                                   │
│       "email": "guest@trial.session"                               │
│     }                                                               │
│   }                                                                 │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 8: FRONTEND - Store Token                                      │
│ File: frontend/src/contexts/AuthContext.tsx:584                    │
│                                                                      │
│ Code:                                                                │
│   storeTokens({                                                     │
│     access_token: result.access_token,                             │
│     ...                                                             │
│   });                                                               │
│   localStorage.setItem('owen_access_token', token);               │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 9: FRONTEND - Now Generate Story                               │
│ File: frontend/src/components/StoryGeneratorModal.tsx:144         │
│                                                                      │
│ Request:                                                             │
│   POST https://backend.../api/story-generator/generate             │
│   Headers: {                                                        │
│     "Authorization": "Bearer eyJhbGc..."  ← Token included!        │
│   }                                                                 │
│   Body: {                                                           │
│     "story_spark": "Phone shows text from tomorrow",               │
│     "reader_emotion": "Spine-tingling chills",                     │
│     "author_vibe": "Stephen King"                                  │
│   }                                                                 │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 10: BACKEND - Story Generator Router                           │
│ File: backend/routers/story_generator_router.py                    │
│                                                                      │
│ - Verifies JWT token (is it valid?)                                │
│ - Checks rate limit (not too many requests?)                       │
│ - Calls LLM service to generate story                              │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 11: LLM SERVICE - Call OpenAI                                  │
│ File: backend/services/llm_service.py                              │
│                                                                      │
│ - Builds prompt with user's inputs                                 │
│ - Calls OpenAI API                                                 │
│ - Waits for AI to generate story (2-5 seconds)                    │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 12: FRONTEND - Display Story                                   │
│ File: frontend/src/components/StoryGeneratorModal.tsx:495         │
│                                                                      │
│ - Shows generated story in modal                                   │
│ - Offers: Copy, Share to X, Insert into editor                    │
│ - User can generate another or close                               │
└─────────────────────────────────────────────────────────────────────┘
```

## The Bug We Fixed (Highlighted)

### Problem Location: STEP 5
```python
# OLD CODE (before fix):
def create_guest_session(self, ip_address, user_agent):
    # ❌ Directly query table without checking if it exists
    recent_guests = self.db.execute_query(
        "SELECT COUNT(*) FROM guest_sessions ..."
    )
    # If table doesn't exist → Query hangs → 10s timeout → Error

# NEW CODE (after fix):
def create_guest_session(self, ip_address, user_agent):
    # ✓ FIRST ensure table exists!
    self._ensure_guest_table_exists()  # ← CREATE TABLE IF NOT EXISTS

    # ✓ NOW query table (we know it exists)
    recent_guests = self.db.execute_query(
        "SELECT COUNT(*) FROM guest_sessions ..."
    )
    # Works perfectly! ✨
```

## Key Files Reference

| Component | File Path | Purpose |
|-----------|-----------|---------|
| Story Generator UI | `frontend/src/components/StoryGeneratorModal.tsx` | User interface |
| Auth Context | `frontend/src/contexts/AuthContext.tsx` | Manages login state |
| API Client | `frontend/src/services/api/client.ts` | Makes HTTP requests |
| Auth Router | `backend/routers/auth_router.py` | Handles /api/auth/* |
| Auth Service | `backend/services/auth_service.py` | Business logic |
| Database Schema | `backend/database/migrations/002_guest_sessions.sql` | Table structure |

## Error Handling Flow

```
Any error at any step:
  │
  ▼
┌────────────────────────────┐
│ Caught by try/catch block  │
└────────────────────────────┘
  │
  ▼
┌────────────────────────────┐
│ Error logged to console    │
│ (for debugging)            │
└────────────────────────────┘
  │
  ▼
┌────────────────────────────┐
│ User-friendly error shown  │
│ "Unable to create session" │
└────────────────────────────┘
  │
  ▼
┌────────────────────────────┐
│ Loading spinner stops      │
│ Button becomes clickable   │
└────────────────────────────┘
```
