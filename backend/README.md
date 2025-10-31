# Owen Voice Analyzer - Backend

Minimal FastAPI backend for Chrome Built-in AI Challenge 2025.

## Features

- **Voice Consistency Analysis**: Gemini-powered character voice analysis
- **Character Profiles**: Store and track character voice traits over time
- **User Authentication**: JWT-based auth with bcrypt password hashing
- **PostgreSQL Database**: Persistent storage for users and profiles

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Set Environment Variables

```bash
cp .env.example .env
# Edit .env and add your keys
```

### 3. Setup Database

```bash
# Create PostgreSQL database
createdb owen_db

# Run migrations
psql owen_db < database/migrations/001_competition_schema.sql
```

### 4. Run Server

```bash
python main.py
# Server runs on http://localhost:8000
```

## API Endpoints

### Authentication

- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token

### Voice Analysis

- `POST /api/voice/analyze` - Analyze text for voice consistency
- `GET /api/voice/profiles` - Get all character profiles
- `DELETE /api/voice/profiles/{name}` - Delete a profile

### Health

- `GET /` - Health check
- `GET /health` - Detailed health status

## Architecture

```
backend/
├── main.py                 # FastAPI app
├── routers/
│   ├── auth_router.py      # Auth endpoints
│   └── character_voice_router.py  # Voice analysis
├── services/
│   ├── auth_service.py     # JWT & password hashing
│   ├── database.py         # PostgreSQL client
│   ├── gemini_service.py   # Gemini API integration
│   └── character_voice_service.py  # Voice analysis logic
├── models/
│   └── schemas.py          # Pydantic models
└── database/
    └── migrations/
        └── 001_competition_schema.sql
```

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@localhost/owen_db` |
| `GEMINI_API_KEY` | Google Gemini API key | `AIza...` |
| `JWT_SECRET` | Secret for JWT tokens | `your-secret-key` |

## Development

```bash
# Run with auto-reload
python main.py

# Or with uvicorn directly
uvicorn main:app --reload --port 8000
```

## Database Schema

### users
- `id` (SERIAL PRIMARY KEY)
- `email` (VARCHAR UNIQUE)
- `password_hash` (VARCHAR)
- `created_at` (TIMESTAMP)

### character_profiles
- `id` (SERIAL PRIMARY KEY)
- `user_id` (INTEGER FK)
- `character_name` (VARCHAR)
- `dialogue_samples` (JSONB)
- `voice_traits` (JSONB)
- `sample_count` (INTEGER)
- `last_updated` (TIMESTAMP)

### documents
- `id` (SERIAL PRIMARY KEY)
- `user_id` (INTEGER FK)
- `title` (VARCHAR)
- `content` (TEXT)
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

## Production Deployment

### Railway

```bash
# Install Railway CLI
npm i -g @railway/cli

# Deploy
railway login
railway init
railway up
```

### Docker

```bash
# Build
docker build -t owen-backend .

# Run
docker run -p 8000:8000 --env-file .env owen-backend
```

## License

MIT
