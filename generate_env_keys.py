#!/usr/bin/env python3
"""
Generate secure environment variables for Owen AI Railway deployment
"""

import secrets
import base64
from cryptography.fernet import Fernet

def generate_jwt_secret():
    """Generate a secure JWT secret key"""
    return secrets.token_urlsafe(64)

def generate_encryption_key():
    """Generate a 32-byte encryption key for database fields"""
    return Fernet.generate_key().decode()

def generate_session_secret():
    """Generate a secure session secret"""
    return secrets.token_urlsafe(32)

def main():
    print("🔐 Generating Secure Environment Variables for Owen AI\n")
    print("=" * 60)
    
    # Generate secure keys
    jwt_secret = generate_jwt_secret()
    db_encryption_key = generate_encryption_key()
    session_secret = generate_session_secret()
    
    print("Copy these values to your Railway environment variables:\n")
    
    print("🔑 JWT_SECRET_KEY:")
    print(f"   {jwt_secret}\n")
    
    print("🔒 DB_ENCRYPTION_KEY:")
    print(f"   {db_encryption_key}\n")
    
    print("🎫 SESSION_SECRET:")
    print(f"   {session_secret}\n")
    
    print("=" * 60)
    print("Railway Commands to Set Environment Variables:")
    print("=" * 60)
    
    print(f'railway env set JWT_SECRET_KEY="{jwt_secret}"')
    print(f'railway env set DB_ENCRYPTION_KEY="{db_encryption_key}"')
    print(f'railway env set SESSION_SECRET="{session_secret}"')
    
    print("\n⚠️  IMPORTANT SECURITY NOTES:")
    print("- Keep these keys secret and never commit them to git")
    print("- Use different keys for development and production")
    print("- Store these keys in a secure password manager")
    print("- Regenerate keys if compromised")
    
    print("\n🚀 Next Steps:")
    print("1. Copy the Railway commands above")
    print("2. Run them in your backend service directory")
    print("3. Add your API keys (OpenAI, Anthropic, Google)")
    print("4. Deploy with 'railway up'")

if __name__ == "__main__":
    main() 