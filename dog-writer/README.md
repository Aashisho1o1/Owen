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
   pip install fastapi uvicorn python-multipart google-generativeai python-dotenv
   ```

4. Create a `.env` file in the backend directory and add your Gemini API key:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
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