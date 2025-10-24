"""
Supabase Authentication module for Disaster Relief Resource Optimizer.
Handles user signup, login, session management, and database operations.
"""

import streamlit as st
import os
from supabase import create_client, Client
import hashlib
import json
from datetime import datetime, timedelta
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase configuration - Try Streamlit secrets first, then environment variables
try:
    SUPABASE_URL = st.secrets.get("SUPABASE_URL", os.getenv("SUPABASE_URL", "YOUR_SUPABASE_PROJECT_URL"))
    SUPABASE_KEY = st.secrets.get("SUPABASE_ANON_KEY", os.getenv("SUPABASE_ANON_KEY", "YOUR_SUPABASE_ANON_KEY"))
    DEMO_MODE = str(st.secrets.get("DEMO_MODE", os.getenv("DEMO_MODE", "true"))).lower() == "true"
except:
    SUPABASE_URL = os.getenv("SUPABASE_URL", "YOUR_SUPABASE_PROJECT_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY", "YOUR_SUPABASE_ANON_KEY")
    DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() == "true"

class SupabaseAuth:
    def __init__(self, url: str = None, key: str = None):
        """Initialize Supabase client."""
        self.supabase_url = url or SUPABASE_URL
        self.supabase_key = key or SUPABASE_KEY
        
        # Check if we should use demo mode
        if DEMO_MODE or self.supabase_url == "YOUR_SUPABASE_PROJECT_URL" or self.supabase_key == "YOUR_SUPABASE_ANON_KEY":
            self.supabase = None
            self.demo_mode = True
            self._init_demo_users()
            print("🎮 Running in DEMO MODE - No Supabase required")
        else:
            try:
                self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
                self.demo_mode = False
                print("🔗 Connected to Supabase successfully")
            except Exception as e:
                st.error(f"Failed to connect to Supabase: {e}")
                self.supabase = None
                self.demo_mode = True
                self._init_demo_users()
                print("⚠️ Falling back to DEMO MODE")
    
    def _init_demo_users(self):
        """Initialize demo users for testing without Supabase."""
        self.demo_users = {
            "admin@disaster.com": {
                "password_hash": self._hash_password("admin123"),
                "created_at": datetime.now().isoformat(),
                "role": "admin"
            },
            "user@disaster.com": {
                "password_hash": self._hash_password("user123"),
                "created_at": datetime.now().isoformat(),
                "role": "user"
            }
        }
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _validate_email(self, email: str) -> bool:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def _validate_password(self, password: str) -> tuple[bool, str]:
        """Validate password strength."""
        if len(password) < 6:
            return False, "Password must be at least 6 characters long"
        if not re.search(r'[A-Za-z]', password):
            return False, "Password must contain at least one letter"
        if not re.search(r'[0-9]', password):
            return False, "Password must contain at least one number"
        return True, "Password is valid"
    
    def signup_user(self, email: str, password: str, confirm_password: str) -> tuple[bool, str]:
        """Sign up a new user."""
        # Validate inputs
        if not email or not password:
            return False, "Email and password are required"
        
        if not self._validate_email(email):
            return False, "Invalid email format"
        
        if password != confirm_password:
            return False, "Passwords do not match"
        
        is_valid, password_msg = self._validate_password(password)
        if not is_valid:
            return False, password_msg
        
        if self.demo_mode:
            return self._signup_demo_user(email, password)
        else:
            return self._signup_supabase_user(email, password)
    
    def _signup_demo_user(self, email: str, password: str) -> tuple[bool, str]:
        """Sign up user in demo mode."""
        if email in self.demo_users:
            return False, "User already exists"
        
        self.demo_users[email] = {
            "password_hash": self._hash_password(password),
            "created_at": datetime.now().isoformat(),
            "role": "user"
        }
        
        return True, "User created successfully in demo mode"
    
    def _signup_supabase_user(self, email: str, password: str) -> tuple[bool, str]:
        """Sign up user using Supabase Auth."""
        try:
            # Sign up with Supabase Auth
            auth_response = self.supabase.auth.sign_up({
                "email": email,
                "password": password
            })
            
            if auth_response.user:
                # Insert additional user data into custom users table
                user_data = {
                    "id": auth_response.user.id,
                    "email": email,
                    "created_at": datetime.now().isoformat(),
                    "role": "user"
                }
                
                self.supabase.table("users").insert(user_data).execute()
                
                return True, "Account created successfully! Please check your email and click the confirmation link before logging in."
            else:
                return False, "Failed to create user"
                
        except Exception as e:
            error_msg = str(e)
            if "User already registered" in error_msg:
                return False, "An account with this email already exists. Please try logging in."
            else:
                return False, f"Signup error: {error_msg}"
    
    def login_user(self, email: str, password: str) -> tuple[bool, str, dict]:
        """Login user and return session data."""
        if not email or not password:
            return False, "Email and password are required", {}
        
        if self.demo_mode:
            return self._login_demo_user(email, password)
        else:
            return self._login_supabase_user(email, password)
    
    def _login_demo_user(self, email: str, password: str) -> tuple[bool, str, dict]:
        """Login user in demo mode."""
        if email not in self.demo_users:
            return False, "User not found", {}
        
        stored_hash = self.demo_users[email]["password_hash"]
        input_hash = self._hash_password(password)
        
        if stored_hash == input_hash:
            user_data = {
                "email": email,
                "role": self.demo_users[email]["role"],
                "created_at": self.demo_users[email]["created_at"],
                "demo_mode": True
            }
            return True, "Login successful", user_data
        else:
            return False, "Invalid credentials", {}
    
    def _login_supabase_user(self, email: str, password: str) -> tuple[bool, str, dict]:
        """Login user using Supabase Auth."""
        try:
            # Try to sign in
            auth_response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if auth_response.user:
                user_data = {
                    "id": auth_response.user.id,
                    "email": email,
                    "demo_mode": False,
                    "email_confirmed": True  # Always set as confirmed for development
                }
                
                # Get additional user data from custom users table
                try:
                    user_response = self.supabase.table("users").select("*").eq("email", email).execute()
                    if user_response.data:
                        user_data.update(user_response.data[0])
                except Exception:
                    pass  # Continue even if users table query fails
                
                return True, "Login successful", user_data
            else:
                return False, "Invalid credentials", {}
                
        except Exception as e:
            error_msg = str(e).lower()
            
            # Handle specific error cases
            if "email not confirmed" in error_msg:
                # For development, create user in our database anyway
                try:
                    # Check if user exists in auth but not confirmed
                    user_data = {
                        "email": email,
                        "demo_mode": False,
                        "email_confirmed": False,
                        "id": f"unconfirmed_{email.replace('@', '_').replace('.', '_')}"
                    }
                    return True, "Login successful (Development mode - email confirmation bypassed)", user_data
                except:
                    return False, "Account exists but email not confirmed. Please contact admin.", {}
            elif "invalid login credentials" in error_msg or "invalid" in error_msg:
                return False, "Invalid email or password. Please try again.", {}
            else:
                return False, f"Login error: {str(e)}", {}
    
    def resend_confirmation(self, email: str) -> tuple[bool, str]:
        """Resend email confirmation."""
        if self.demo_mode:
            return True, "Demo mode - no email confirmation needed"
        
        try:
            self.supabase.auth.resend({
                "type": "signup",
                "email": email
            })
            return True, "Confirmation email sent! Please check your inbox."
        except Exception as e:
            return False, f"Error sending confirmation: {str(e)}"
    
    def logout_user(self) -> tuple[bool, str]:
        """Logout current user."""
        if self.demo_mode:
            return True, "Logged out successfully"
        else:
            try:
                self.supabase.auth.sign_out()
                return True, "Logged out successfully"
            except Exception as e:
                return False, f"Logout error: {str(e)}"
    
    def get_current_user(self) -> dict:
        """Get current user session data."""
        if self.demo_mode:
            return st.session_state.get('user_data', {})
        else:
            try:
                user = self.supabase.auth.get_user()
                if user:
                    return {"id": user.user.id, "email": user.user.email}
                return {}
            except:
                return {}

def init_session_state():
    """Initialize session state variables."""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_data' not in st.session_state:
        st.session_state.user_data = {}
    if 'auth_instance' not in st.session_state:
        st.session_state.auth_instance = SupabaseAuth()

def show_login_page():
    """Display login page."""
    st.title("🔐 Login to Disaster Relief Optimizer")
    
    # Demo mode notice
    if st.session_state.auth_instance.demo_mode:
        st.info("""
        **Demo Mode Active**
        
        Supabase credentials not configured. Using demo authentication.
        
        Demo Accounts:
        - **Admin**: admin@disaster.com / admin123
        - **User**: user@disaster.com / user123
        
        Or create a new demo account below.
        """)
    else:
        st.info("""
        **Supabase Authentication Active**
        
        💡 **Quick Test Account:**
        - Email: test@disaster.com
        - Password: test123
        
        Or signup for a new account below.
        """)
    
    with st.form("login_form"):
        email = st.text_input("Email", value="test@disaster.com")
        password = st.text_input("Password", type="password", value="test123")
        
        col1, col2 = st.columns(2)
        
        with col1:
            login_button = st.form_submit_button("Login")
        
        with col2:
            if st.form_submit_button("Go to Signup"):
                st.session_state.show_signup = True
                st.rerun()
    
    if login_button:
        success, message, user_data = st.session_state.auth_instance.login_user(email, password)
        
        if success:
            st.session_state.authenticated = True
            st.session_state.user_data = user_data
            st.success(message)
            st.rerun()
        else:
            st.error(message)

def show_signup_page():
    """Display signup page."""
    st.title("📝 Sign Up for Disaster Relief Optimizer")
    
    # Demo mode notice
    if st.session_state.auth_instance.demo_mode:
        st.info("**Demo Mode**: Creating demo account for testing purposes.")
    
    with st.form("signup_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        
        col1, col2 = st.columns(2)
        
        with col1:
            signup_button = st.form_submit_button("Sign Up")
        
        with col2:
            if st.form_submit_button("Back to Login"):
                st.session_state.show_signup = False
                st.rerun()
    
    if signup_button:
        success, message = st.session_state.auth_instance.signup_user(email, password, confirm_password)
        
        if success:
            st.success(message)
            st.info("You can now login with your credentials.")
            if st.button("Go to Login"):
                st.session_state.show_signup = False
                st.rerun()
        else:
            st.error(message)

def show_user_info():
    """Display current user information in sidebar."""
    if st.session_state.authenticated:
        user_data = st.session_state.user_data
        
        st.sidebar.markdown("---")
        st.sidebar.subheader("👤 User Info")
        st.sidebar.write(f"**Email**: {user_data.get('email', 'N/A')}")
        
        if user_data.get('role'):
            st.sidebar.write(f"**Role**: {user_data['role'].title()}")
        
        if user_data.get('demo_mode'):
            st.sidebar.write("**Mode**: Demo")
        
        if st.sidebar.button("🚪 Logout"):
            success, message = st.session_state.auth_instance.logout_user()
            if success:
                st.session_state.authenticated = False
                st.session_state.user_data = {}
                st.rerun()
            else:
                st.sidebar.error(message)

def require_authentication(app_function):
    """Decorator to require authentication for app functions."""
    def wrapper(*args, **kwargs):
        init_session_state()
        
        if not st.session_state.authenticated:
            # Show signup or login page
            if st.session_state.get('show_signup', False):
                show_signup_page()
            else:
                show_login_page()
        else:
            # Show the main app
            show_user_info()
            return app_function(*args, **kwargs)
    
    return wrapper

# SQL Schema for Supabase
SUPABASE_SQL_SCHEMA = """
-- SQL Schema for Disaster Relief Resource Optimizer
-- Paste this into your Supabase SQL Editor

-- Enable RLS (Row Level Security)
ALTER TABLE IF EXISTS users ENABLE ROW LEVEL SECURITY;

-- Create users table for additional user data
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    role TEXT DEFAULT 'user' CHECK (role IN ('user', 'admin')),
    full_name TEXT,
    organization TEXT,
    last_login TIMESTAMP WITH TIME ZONE
);

-- Create predictions table to store ML predictions
CREATE TABLE IF NOT EXISTS predictions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    disaster_type TEXT NOT NULL,
    state TEXT,
    district TEXT,
    people_affected INTEGER,
    deaths INTEGER,
    damages BIGINT,
    predicted_severity TEXT CHECK (predicted_severity IN ('Low', 'Medium', 'High')),
    prediction_confidence JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create resource_allocations table to store allocation results
CREATE TABLE IF NOT EXISTS resource_allocations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    prediction_id UUID REFERENCES predictions(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    food_kits_allocated INTEGER DEFAULT 0,
    water_packs_allocated INTEGER DEFAULT 0,
    medicine_kits_allocated INTEGER DEFAULT 0,
    shelter_units_allocated INTEGER DEFAULT 0,
    fulfillment_rate DECIMAL(5,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_predictions_user_id ON predictions(user_id);
CREATE INDEX IF NOT EXISTS idx_predictions_created_at ON predictions(created_at);
CREATE INDEX IF NOT EXISTS idx_resource_allocations_user_id ON resource_allocations(user_id);

-- RLS Policies
-- Users can only see their own data
CREATE POLICY "Users can view own data" ON users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own data" ON users
    FOR UPDATE USING (auth.uid() = id);

-- Predictions policies
CREATE POLICY "Users can view own predictions" ON predictions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own predictions" ON predictions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Resource allocations policies
CREATE POLICY "Users can view own allocations" ON resource_allocations
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own allocations" ON resource_allocations
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Function to automatically set updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to automatically update updated_at
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Insert default admin user (optional)
-- INSERT INTO users (email, role, full_name) 
-- VALUES ('admin@disaster.com', 'admin', 'System Administrator')
-- ON CONFLICT (email) DO NOTHING;
"""

# Global instance for easy access
_auth_instance = None

def get_supabase_client():
    """Get Supabase client instance for database operations."""
    global _auth_instance
    if _auth_instance is None:
        _auth_instance = SupabaseAuth()
    return _auth_instance.supabase if _auth_instance and not _auth_instance.demo_mode else None

def get_auth_instance():
    """Get the global SupabaseAuth instance."""
    global _auth_instance
    if _auth_instance is None:
        _auth_instance = SupabaseAuth()
    return _auth_instance

if __name__ == "__main__":
    # Print SQL schema for easy copying
    print("=== SUPABASE SQL SCHEMA ===")
    print("Copy and paste the following SQL into your Supabase SQL Editor:")
    print("=" * 50)
    print(SUPABASE_SQL_SCHEMA)