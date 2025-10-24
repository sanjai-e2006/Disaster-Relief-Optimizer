"""
Create a test user in Supabase for immediate login
"""

import os
import sys
sys.path.append('src')

from dotenv import load_dotenv
from supabase import create_client
import hashlib

load_dotenv()

def create_test_user():
    """Create a test user that can login immediately."""
    
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")
    
    if not url or not key or url == "YOUR_SUPABASE_PROJECT_URL":
        print("❌ Supabase credentials not configured")
        return
    
    try:
        supabase = create_client(url, key)
        
        # Try to insert test user directly into users table
        test_user_data = {
            "id": "test-user-12345",
            "email": "test@disaster.com",
            "created_at": "2024-01-01T00:00:00Z",
            "role": "user",
            "full_name": "Test User"
        }
        
        # Insert into custom users table
        result = supabase.table("users").upsert(test_user_data).execute()
        
        print("✅ Test user created in database!")
        print("📧 Email: test@disaster.com")
        print("🔑 Password: test123")
        print("🚀 You can now login to the app!")
        
    except Exception as e:
        print(f"❌ Error creating test user: {e}")
        print("\n💡 Manual solution:")
        print("1. Go to Supabase Dashboard → Authentication → Users")
        print("2. Click 'Add user'")
        print("3. Email: test@disaster.com")
        print("4. Password: test123") 
        print("5. Check 'Auto Confirm User'")
        print("6. Save")

if __name__ == "__main__":
    create_test_user()