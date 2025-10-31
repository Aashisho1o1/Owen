# Quick Start - Owen Voice Analyzer

**Get up and running in 5 minutes!**

## 1. Get Gemini API Key (1 minute)

Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
- Click "Create API Key"
- Copy the key (starts with `AIza...`)

## 2. Run Frontend (2 minutes)

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173)

## 3. Enter API Key (30 seconds)

- Paste your Gemini API key
- Click "Initialize"
- Key is saved to localStorage

## 4. Start Writing! (1 minute)

Try this example:

```
Jake: "Listen up. We got five minutes."
Emma: "But what about the plan?"
Jake: "No time for questions. Move!"
```

**What happens**:
- After 2 seconds, auto-analysis runs
- Character profiles appear on right
- Consistency scores shown
- Voice traits identified

## 5. Test Inconsistency (30 seconds)

Now try this:

```
Emma: "Hey! Like, totally cool!"
Emma: "I must express my profound disagreement with your proposition."
Emma: "Whatever, dude."
```

**What happens**:
- Low consistency score (40-50%)
- Issues listed
- Suggestions provided

## Done! 🎉

You now have a working voice consistency checker!

---

## Optional: Run Backend

For profile persistence and multi-user support:

### Setup Database

```bash
createdb owen_db
psql owen_db < backend/database/migrations/001_competition_schema.sql
```

### Configure Environment

```bash
cd backend
cp .env.example .env

# Edit .env:
DATABASE_URL=postgresql://user:pass@localhost/owen_db
GEMINI_API_KEY=your_gemini_key_here
JWT_SECRET=your-secret-key
```

### Run Server

```bash
pip install -r requirements.txt
python main.py
```

Backend runs on [http://localhost:8000](http://localhost:8000)

---

## Troubleshooting

### Build fails

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

### API key not working

- Check key starts with `AIza`
- Get new key from Google AI Studio
- Clear localStorage: `localStorage.clear()`

### Backend connection issues

- Check backend is running: `curl http://localhost:8000/health`
- Check DATABASE_URL in .env
- Check PostgreSQL is running: `pg_isready`

---

## Need Help?

See [COMPLETE_SUMMARY.md](COMPLETE_SUMMARY.md) for full documentation.
