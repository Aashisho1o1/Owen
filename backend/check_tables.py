#!/usr/bin/env python3
"""
Quick diagnostic script to check database tables
"""

import os
import sys

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from services.database import get_db_service

def check_tables():
    """Check if required tables exist"""
    print("🔍 Checking database tables...")

    db = get_db_service()

    # Check for guest_sessions table
    try:
        result = db.execute_query("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = 'guest_sessions'
            );
        """, fetch='one')

        exists = list(result.values())[0] if result else False

        if exists:
            print("✅ guest_sessions table EXISTS")

            # Check count
            count_result = db.execute_query(
                "SELECT COUNT(*) as count FROM guest_sessions",
                fetch='one'
            )
            print(f"   Total guest sessions: {count_result['count']}")
        else:
            print("❌ guest_sessions table DOES NOT EXIST")
            print("\n💡 This is the problem! The backend code expects this table.")
            print("   Solution: Run the migration SQL file to create it.")

    except Exception as e:
        print(f"❌ Error checking guest_sessions table: {e}")

    # Check other tables
    print("\n📋 Checking other tables:")
    try:
        result = db.execute_query("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """, fetch='all')

        for row in result:
            print(f"   ✅ {row['table_name']}")

    except Exception as e:
        print(f"❌ Error listing tables: {e}")

if __name__ == "__main__":
    check_tables()
