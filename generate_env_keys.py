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
    
    # Generate encryption key for .env file
    env_encryption_key = Fernet.generate_key()
    cipher = Fernet(env_encryption_key)
    
    # Encrypt sensitive data
    encrypted_jwt_secret = cipher.encrypt(jwt_secret.encode()).decode()
    encrypted_db_encryption_key = cipher.encrypt(db_encryption_key.encode()).decode()
    encrypted_session_secret = cipher.encrypt(session_secret.encode()).decode()
    
    # Write encrypted keys to a secure .env file
    env_file_path = ".env"
    with open(env_file_path, "w") as env_file:
        env_file.write(f"JWT_SECRET_KEY={encrypted_jwt_secret}\n")
        env_file.write(f"DB_ENCRYPTION_KEY={encrypted_db_encryption_key}\n")
        env_file.write(f"SESSION_SECRET={encrypted_session_secret}\n")
    
    # Save encryption key securely (instructions provided to user)
    encryption_key_path = ".env.key"
    with open(encryption_key_path, "w") as key_file:
        key_file.write(env_encryption_key.decode())
    
    # Set restrictive permissions on the file
    import os
    os.chmod(env_file_path, 0o600)
    
    print(f"✅ Secure environment variables have been written to '{env_file_path}'.")
    print("   Please ensure this file is stored securely and not committed to version control.\n")
    
    print("⚠️  IMPORTANT SECURITY NOTES:")
    print("- Keep the .env file and .env.key secure and never commit them to git")
    print("- Use different keys for development and production")
    print("- Store these keys in a secure password manager")
    print("- Regenerate keys if compromised")
    
    print("\n🚀 Next Steps:")
    print("1. Use the .env file to configure your environment")
    print("2. Add your API keys (OpenAI, Anthropic, Google)")
    print("3. Deploy with 'railway up'")

if __name__ == "__main__":
    main() 