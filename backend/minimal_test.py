#!/usr/bin/env python3
"""
Minimal FastAPI app to test CORS without complex dependencies
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Minimal CORS Test")

# Add CORS middleware first
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://frontend-production-e178.up.railway.app",
        "https://frontend-production-88b0.up.railway.app", 
        "http://localhost:3000",
        "*"  # Allow all for testing
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

@app.options("/{path:path}")
async def preflight_handler(path: str):
    """Handle CORS preflight requests"""
    return {"message": "OK"}

@app.get("/")
async def root():
    return {
        "message": "Minimal CORS test - working!",
        "status": "healthy"
    }

@app.get("/api/health")
async def health():
    return {
        "status": "healthy",
        "message": "Minimal backend working",
        "cors_test": "success"
    }

@app.get("/test")
async def test():
    return {"test": "success", "cors": "working"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port) 