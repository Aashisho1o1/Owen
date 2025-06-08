# 🚀 Railway Deployment Guide for Owen AI Writing Assistant

## 📋 Prerequisites

✅ Railway CLI installed (version 4.5.3)  
✅ Railway account created  
✅ Git repository with your code  
⏳ Railway authentication completed

## 🏗️ Deployment Architecture

```
Owen AI Application
├── Backend Service (FastAPI + Security)
│   ├── Port: Auto-assigned by Railway
│   ├── Database: SQLite (will upgrade to PostgreSQL)
│   └── Environment: Production
└── Frontend Service (React + Vite)
    ├── Port: Auto-assigned by Railway  
    ├── API Connection: Backend service URL
    └── Static Files: Served by Railway
```

## 🔧 Step-by-Step Deployment

### Step 1: Authentication
```bash
railway login
# Opens browser for authentication
```

### Step 2: Initialize Railway Project
```bash
railway init
# Enter project name: owen-ai-assistant
# Select workspace and confirm
```

### Step 3: Deploy Backend Service First
```bash
# Navigate to backend directory
cd dog-writer/backend

# Deploy the backend service
railway up

# After deployment, get the service URL
railway status
```

### Step 4: Set Environment Variables for Backend
```bash
# Set security environment variables (use generated keys)
railway variables set JWT_SECRET_KEY="your-generated-jwt-secret"
railway variables set DB_ENCRYPTION_KEY="your-generated-encryption-key"
railway variables set SESSION_SECRET="your-generated-session-secret"

# Set API keys (replace with your actual keys)
railway variables set OPENAI_API_KEY="sk-your-openai-key"
railway variables set ANTHROPIC_API_KEY="sk-ant-your-anthropic-key"
railway variables set GOOGLE_API_KEY="your-google-gemini-key"

# Set CORS origin for frontend (will update after frontend deployment)
railway variables set FRONTEND_URL="https://your-frontend-url.railway.app"
```

### Step 5: Deploy Frontend Service
```bash
# Navigate to frontend directory  
cd ../frontend

# Add the frontend as a new service
railway service

# Set backend API URL environment variable
railway variables set VITE_API_URL="https://your-backend-url.railway.app"

# Deploy frontend
railway up
```

### Step 6: Update Backend CORS Settings
```bash
# Go back to backend
cd ../backend

# Update frontend URL in backend environment
railway variables set FRONTEND_URL="https://your-actual-frontend-url.railway.app"

# Redeploy backend with updated CORS
railway redeploy
```

## 🔒 Required Environment Variables

### Backend Service
| Variable | Description | Example |
|----------|-------------|---------|
| `JWT_SECRET_KEY` | JWT token signing key | `super-secure-random-string-here` |
| `DB_ENCRYPTION_KEY` | Database field encryption | `32-byte-base64-encoded-key` |
| `OPENAI_API_KEY` | OpenAI API access | `sk-...` |
| `ANTHROPIC_API_KEY` | Anthropic API access | `sk-ant-...` |
| `GOOGLE_API_KEY` | Google Gemini API | `AI...` |
| `FRONTEND_URL` | Frontend domain | `https://your-frontend.railway.app` |

### Frontend Service  
| Variable | Description | Example |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL | `https://your-backend.railway.app` |

## 🚀 Final URLs

After deployment, you'll get:
- **Backend API**: `https://[service-name].railway.app`
- **Frontend App**: `https://[frontend-service].railway.app`  
- **API Docs**: `https://[service-name].railway.app/docs`

## 🔧 Production Configuration

### Security Features Active:
✅ JWT Authentication with secure tokens  
✅ Input validation and XSS prevention  
✅ Database field-level encryption  
✅ Rate limiting and abuse prevention  
✅ CORS properly configured for production  

### Performance Optimizations:
✅ Optimized React state management  
✅ Database connection pooling  
✅ Debounced user inputs  
✅ Memoized expensive operations  

## 🐛 Troubleshooting

### Common Issues:
1. **Build fails**: Check requirements.txt and package.json
2. **CORS errors**: Update FRONTEND_URL environment variable
3. **Database errors**: Ensure encryption key is set
4. **Authentication issues**: Verify JWT_SECRET_KEY is secure

### Useful Railway Commands:
```bash
railway status      # Check service status and URLs
railway logs        # View service logs
railway variables   # List environment variables
railway service     # Manage services
railway open        # Open Railway dashboard
railway redeploy    # Redeploy service
```

## 📊 Expected Performance

- **Response Time**: < 200ms for API calls
- **Security**: Enterprise-grade with JWT + encryption
- **Availability**: 99.9% uptime on Railway
- **Scalability**: Auto-scaling based on traffic

## 🎯 Next Steps After Deployment

1. ✅ Test all API endpoints
2. ✅ Verify frontend-backend communication  
3. ✅ Test user authentication flow
4. ✅ Monitor performance metrics
5. ✅ Set up custom domain (optional)

---

**Your Owen AI Writing Assistant will be live at the Railway URLs!** 🎉 