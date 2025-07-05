# AI Writer's Assistant

An AI-powered collaborative writing assistant that allows users to write text and get feedback from an AI persona mimicking a famous author.

## Features

- Side-by-side interface with a rich text editor and chat interface
- AI author personas (Ernest Hemingway, Jane Austen, Virginia Woolf)
- Different help focuses (Dialogue Writing, Scene Description, Plot Development, etc.)
- Checkpoint saving feature

## Setup

### Prerequisites

- Python 3.8+ with pip
- Node.js and npm
- Gemini API key (from Google AI Studio)

### Backend Setup

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   # or
   venv\Scripts\activate     # On Windows
   ```

3. Install dependencies:
   ```
   pip install fastapi uvicorn python-multipart google-generativeai python-dotenv google-cloud-speech==2.22.0
   ```

4. Create a `.env` file in the backend directory and add your Gemini API key:
   ```
   GEMINI_API_KEY=your_gemini_api_key
   ```

5. Start the FastAPI server:
   ```
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Start the development server:
   ```
   npm run dev
   ```

4. Open your browser and navigate to the URL shown in the terminal (typically http://localhost:5173)

## Using the Application

1. Select an author persona and help focus from the dropdown menus
2. Write in the rich text editor on the left
3. Ask questions or request help in the chat input on the right
4. The AI will respond in the style of the selected author and may provide fill-in-the-blank suggestions
5. Use the "Save Checkpoint" button to save your progress

## Technologies Used

- **Backend**: FastAPI, Google Generative AI (Gemini API)
- **Frontend**: React, TipTap (rich text editor), Axios (for API requests)

## Future Enhancements

- User authentication
- Persistent storage of checkpoints
- More author personas
- Enhanced editor features

<!-- Test commit to verify connection to OwenWrites organization repository. -->

# DOG Writer - AI Writing Assistant

A full-stack AI writing assistant built with FastAPI backend and React frontend, deployed on Railway.

## 🚨 **CRITICAL SECURITY SETUP FOR PRODUCTION**

### **JWT_SECRET_KEY Configuration**

**⚠️ MANDATORY**: Before deploying to production, you **MUST** set a secure JWT_SECRET_KEY in Railway:

1. **Generate a secure key**:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(64))"
   ```

2. **Set in Railway Dashboard**:
   - Go to Railway Dashboard → Your Project → Backend Service
   - Navigate to "Variables" tab
   - Add new environment variable:
     - **Name**: `JWT_SECRET_KEY`
     - **Value**: [The generated key from step 1]

3. **Why this is critical**:
   - Without this, users will be randomly logged out on every deployment
   - Auto-generated keys are not persistent across restarts
   - This is a **blocking security vulnerability** for production use

### **Deployment Will Fail** if JWT_SECRET_KEY is not set

The application is configured to **fail startup** if JWT_SECRET_KEY is not properly configured. This prevents the security vulnerability of auto-generated keys.

---

## 🚀 **Features**

- **AI Writing Assistance**: Powered by OpenAI GPT and Google Gemini
- **Document Management**: Create, edit, and organize documents
- **Template System**: Fiction writing templates (novels, screenplays, etc.)
- **Folder Organization**: Hierarchical document organization
- **Grammar Checking**: Integrated grammar and style suggestions
- **Real-time Collaboration**: Live editing with auto-save
- **Responsive Design**: Works on desktop and mobile devices

## 🛠 **Tech Stack**

**Backend**:
- FastAPI (Python)
- PostgreSQL (Railway)
- JWT Authentication
- OpenAI & Gemini APIs
- Hypercorn (ASGI server)

**Frontend**:
- React + TypeScript
- Vite (build tool)
- Tailwind CSS
- Axios (HTTP client)

**Deployment**:
- Railway (Backend + Database)
- Railway (Frontend)
- Environment-based configuration

## 🔧 **Local Development**

### **Prerequisites**
- Python 3.11+
- Node.js 18+
- PostgreSQL (or use Railway database)

### **Backend Setup**
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env  # Configure your environment variables
python main.py
```

### **Frontend Setup**
```bash
cd frontend
npm install
npm run dev
```

### **Environment Variables**
```env
# Backend (.env)
DATABASE_URL=postgresql://user:password@localhost:5432/dogwriter
JWT_SECRET_KEY=your-super-secure-jwt-secret-key-here
OPENAI_API_KEY=your-openai-api-key
GEMINI_API_KEY=your-gemini-api-key

# Frontend (.env)
VITE_API_URL=http://localhost:8000
```

## 📁 **Project Structure**

```
DOG/
├── backend/                 # FastAPI backend
│   ├── main.py             # Application entry point
│   ├── routers/            # API route handlers
│   ├── services/           # Business logic
│   ├── models/             # Database models
│   └── requirements.txt    # Python dependencies
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── services/       # API services
│   │   ├── hooks/          # Custom React hooks
│   │   └── styles/         # CSS styles
│   └── package.json        # Node.js dependencies
└── README.md
```

## 🚀 **Deployment**

### **Railway Deployment**

1. **Backend**: Automatically deployed from `backend/` directory
2. **Frontend**: Automatically deployed from `frontend/` directory  
3. **Database**: PostgreSQL service on Railway

### **Environment Variables (Railway)**
Set these in Railway Dashboard → Variables:

**Backend**:
- `JWT_SECRET_KEY` (CRITICAL - see security section above)
- `DATABASE_URL` (auto-configured by Railway)
- `OPENAI_API_KEY`
- `GEMINI_API_KEY`

**Frontend**:
- `VITE_API_URL` (your backend Railway URL)

## 📊 **API Endpoints**

### **Authentication**
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Refresh access token

### **Documents**
- `GET /api/documents` - List user documents
- `POST /api/documents` - Create new document
- `PUT /api/documents/{id}` - Update document
- `DELETE /api/documents/{id}` - Delete document

### **AI Features**
- `POST /api/chat` - AI writing assistance
- `POST /api/grammar/check` - Grammar checking

### **Templates**
- `GET /api/fiction-templates` - List writing templates
- `POST /api/fiction-templates/{id}/create` - Create from template

## 🔐 **Security Features**

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: bcrypt for password security
- **Rate Limiting**: Prevents API abuse
- **CORS Configuration**: Secure cross-origin requests
- **Input Validation**: Sanitized user inputs
- **SQL Injection Prevention**: Parameterized queries

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 **Support**

For issues and questions:
- Open an issue on GitHub
- Check the documentation
- Review the Railway deployment logs

---

**Made with ❤️ for writers everywhere** 