"""
User Profile Management System
Handles user roles, preferences, and activity tracking
"""

import streamlit as st
from datetime import datetime, timedelta
import json
import os
from typing import Dict, Optional, List
import sys

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from auth import get_supabase_client, get_auth_instance

class UserProfileManager:
    """Manages user profiles, roles, and preferences."""
    
    def __init__(self):
        self.supabase = get_supabase_client()
        self.auth_instance = get_auth_instance()
        self.profiles_file = "data/user_profiles.json"
        self.activity_file = "data/user_activity.json"
        
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        
        # Initialize files if they don't exist
        self._initialize_files()
    
    def _initialize_files(self):
        """Initialize JSON files if they don't exist."""
        if not os.path.exists(self.profiles_file):
            with open(self.profiles_file, 'w') as f:
                json.dump({}, f)
        
        if not os.path.exists(self.activity_file):
            with open(self.activity_file, 'w') as f:
                json.dump({}, f)
    
    def _load_profiles(self) -> Dict:
        """Load user profiles from JSON file."""
        try:
            with open(self.profiles_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def _save_profiles(self, profiles: Dict):
        """Save user profiles to JSON file."""
        try:
            with open(self.profiles_file, 'w') as f:
                json.dump(profiles, f, indent=2, default=str)
        except Exception as e:
            st.error(f"Error saving profiles: {e}")
    
    def _load_activity(self) -> Dict:
        """Load user activity from JSON file."""
        try:
            with open(self.activity_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def _save_activity(self, activity: Dict):
        """Save user activity to JSON file."""
        try:
            with open(self.activity_file, 'w') as f:
                json.dump(activity, f, indent=2, default=str)
        except Exception as e:
            st.error(f"Error saving activity: {e}")
    
    def create_profile(self, user_id: str, email: str, role: str = "user") -> Dict:
        """Create a new user profile."""
        profiles = self._load_profiles()
        
        profile = {
            "user_id": user_id,
            "email": email,
            "role": role,  # "admin", "manager", "user"
            "created_at": datetime.now().isoformat(),
            "last_login": datetime.now().isoformat(),
            "preferences": {
                "theme": "light",
                "dashboard_layout": "default",
                "notifications": True,
                "auto_refresh": True,
                "default_view": "dashboard"
            },
            "permissions": self._get_role_permissions(role),
            "stats": {
                "predictions_made": 0,
                "disasters_processed": 0,
                "resources_allocated": 0,
                "login_count": 1
            }
        }
        
        profiles[user_id] = profile
        self._save_profiles(profiles)
        return profile
    
    def _get_role_permissions(self, role: str) -> List[str]:
        """Get permissions based on user role."""
        permissions = {
            "admin": [
                "view_dashboard", "make_predictions", "bulk_processing", 
                "view_analytics", "manage_users", "export_data", 
                "system_settings", "view_all_activities"
            ],
            "manager": [
                "view_dashboard", "make_predictions", "bulk_processing", 
                "view_analytics", "export_data", "view_team_activities"
            ],
            "user": [
                "view_dashboard", "make_predictions", "view_analytics"
            ]
        }
        return permissions.get(role, permissions["user"])
    
    def get_profile(self, user_id: str) -> Optional[Dict]:
        """Get user profile by user ID."""
        profiles = self._load_profiles()
        return profiles.get(user_id)
    
    def update_profile(self, user_id: str, updates: Dict):
        """Update user profile."""
        profiles = self._load_profiles()
        if user_id in profiles:
            profiles[user_id].update(updates)
            profiles[user_id]["updated_at"] = datetime.now().isoformat()
            self._save_profiles(profiles)
    
    def update_last_login(self, user_id: str):
        """Update user's last login time."""
        profiles = self._load_profiles()
        if user_id in profiles:
            profiles[user_id]["last_login"] = datetime.now().isoformat()
            profiles[user_id]["stats"]["login_count"] += 1
            self._save_profiles(profiles)
    
    def log_activity(self, user_id: str, activity_type: str, details: Dict = None):
        """Log user activity."""
        activity_data = self._load_activity()
        
        if user_id not in activity_data:
            activity_data[user_id] = []
        
        activity = {
            "timestamp": datetime.now().isoformat(),
            "type": activity_type,
            "details": details or {}
        }
        
        activity_data[user_id].append(activity)
        
        # Keep only last 100 activities per user
        if len(activity_data[user_id]) > 100:
            activity_data[user_id] = activity_data[user_id][-100:]
        
        self._save_activity(activity_data)
    
    def get_user_activity(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Get user activity history."""
        activity_data = self._load_activity()
        activities = activity_data.get(user_id, [])
        return activities[-limit:] if activities else []
    
    def increment_stat(self, user_id: str, stat_name: str, amount: int = 1):
        """Increment a user statistic."""
        profiles = self._load_profiles()
        if user_id in profiles:
            if stat_name in profiles[user_id]["stats"]:
                profiles[user_id]["stats"][stat_name] += amount
            else:
                profiles[user_id]["stats"][stat_name] = amount
            self._save_profiles(profiles)
    
    def get_all_users(self) -> Dict:
        """Get all user profiles (admin only)."""
        return self._load_profiles()
    
    def has_permission(self, user_id: str, permission: str) -> bool:
        """Check if user has specific permission."""
        profile = self.get_profile(user_id)
        if not profile:
            return False
        return permission in profile.get("permissions", [])

def create_profile_interface():
    """Create user profile management interface."""
    st.subheader("👤 User Profile Management")
    
    # Get current user from session
    if 'user' not in st.session_state:
        st.error("Please log in to access profile settings.")
        return
    
    user_info = st.session_state.user
    user_id = user_info.get('id', 'unknown')
    email = user_info.get('email', 'unknown@example.com')
    
    # Initialize profile manager
    profile_manager = UserProfileManager()
    
    # Get or create profile
    profile = profile_manager.get_profile(user_id)
    if not profile:
        profile = profile_manager.create_profile(user_id, email)
        st.success("✅ Profile created successfully!")
    
    # Profile tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Profile Info", "⚙️ Preferences", "📊 Activity", "🔧 Admin"])
    
    with tab1:
        st.markdown("### 📋 Profile Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 10px; margin: 1rem 0;">
                <h4>👤 User Details</h4>
                <p><strong>Email:</strong> {email}</p>
                <p><strong>Role:</strong> {profile.get('role', 'user').title()}</p>
                <p><strong>Member Since:</strong> {profile.get('created_at', 'Unknown')[:10]}</p>
                <p><strong>Last Login:</strong> {profile.get('last_login', 'Unknown')[:10]}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            stats = profile.get('stats', {})
            st.markdown(f"""
            <div style="background: #e3f2fd; padding: 1.5rem; border-radius: 10px; margin: 1rem 0;">
                <h4>📊 Usage Statistics</h4>
                <p><strong>Predictions Made:</strong> {stats.get('predictions_made', 0)}</p>
                <p><strong>Disasters Processed:</strong> {stats.get('disasters_processed', 0)}</p>
                <p><strong>Resources Allocated:</strong> {stats.get('resources_allocated', 0)}</p>
                <p><strong>Login Count:</strong> {stats.get('login_count', 0)}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Permissions
        st.markdown("### 🔐 Permissions")
        permissions = profile.get('permissions', [])
        
        col1, col2 = st.columns(2)
        with col1:
            for i, perm in enumerate(permissions[:len(permissions)//2]):
                st.success(f"✅ {perm.replace('_', ' ').title()}")
        
        with col2:
            for perm in permissions[len(permissions)//2:]:
                st.success(f"✅ {perm.replace('_', ' ').title()}")
    
    with tab2:
        st.markdown("### ⚙️ User Preferences")
        
        preferences = profile.get('preferences', {})
        
        col1, col2 = st.columns(2)
        
        with col1:
            theme = st.selectbox(
                "🎨 Theme",
                ["light", "dark"],
                index=0 if preferences.get('theme') == 'light' else 1
            )
            
            dashboard_layout = st.selectbox(
                "📱 Dashboard Layout",
                ["default", "compact", "expanded"],
                index=["default", "compact", "expanded"].index(preferences.get('dashboard_layout', 'default'))
            )
        
        with col2:
            notifications = st.checkbox(
                "🔔 Enable Notifications",
                value=preferences.get('notifications', True)
            )
            
            auto_refresh = st.checkbox(
                "🔄 Auto Refresh Dashboard",
                value=preferences.get('auto_refresh', True)
            )
            
            default_view = st.selectbox(
                "🏠 Default View",
                ["dashboard", "prediction", "analytics"],
                index=["dashboard", "prediction", "analytics"].index(preferences.get('default_view', 'dashboard'))
            )
        
        if st.button("💾 Save Preferences", type="primary"):
            new_preferences = {
                "theme": theme,
                "dashboard_layout": dashboard_layout,
                "notifications": notifications,
                "auto_refresh": auto_refresh,
                "default_view": default_view
            }
            
            profile_manager.update_profile(user_id, {"preferences": new_preferences})
            st.success("✅ Preferences saved successfully!")
            st.rerun()
    
    with tab3:
        st.markdown("### 📊 Recent Activity")
        
        activities = profile_manager.get_user_activity(user_id, limit=20)
        
        if activities:
            for activity in reversed(activities[-10:]):  # Show last 10 activities
                timestamp = activity.get('timestamp', '')[:19]
                activity_type = activity.get('type', 'Unknown')
                details = activity.get('details', {})
                
                with st.expander(f"🕒 {timestamp} - {activity_type.title()}"):
                    if details:
                        for key, value in details.items():
                            st.write(f"**{key.replace('_', ' ').title()}:** {value}")
                    else:
                        st.write("No additional details")
        else:
            st.info("📝 No recent activity found.")
    
    with tab4:
        if profile_manager.has_permission(user_id, "manage_users"):
            st.markdown("### 🔧 Admin Panel")
            
            all_users = profile_manager.get_all_users()
            
            st.markdown("#### 👥 All Users")
            
            user_data = []
            for uid, user_profile in all_users.items():
                user_data.append({
                    "Email": user_profile.get('email', 'Unknown'),
                    "Role": user_profile.get('role', 'user').title(),
                    "Last Login": user_profile.get('last_login', 'Unknown')[:10],
                    "Predictions": user_profile.get('stats', {}).get('predictions_made', 0),
                    "Login Count": user_profile.get('stats', {}).get('login_count', 0)
                })
            
            if user_data:
                import pandas as pd
                df = pd.DataFrame(user_data)
                st.dataframe(df, use_container_width=True)
            
            # User management actions
            st.markdown("#### ⚙️ User Management")
            
            selected_user = st.selectbox(
                "Select User to Manage",
                options=list(all_users.keys()),
                format_func=lambda x: all_users[x].get('email', x)
            )
            
            if selected_user and selected_user in all_users:
                current_role = all_users[selected_user].get('role', 'user')
                new_role = st.selectbox(
                    f"Change Role for {all_users[selected_user].get('email')}",
                    ["user", "manager", "admin"],
                    index=["user", "manager", "admin"].index(current_role)
                )
                
                if st.button("🔄 Update Role", type="primary"):
                    profile_manager.update_profile(selected_user, {
                        "role": new_role,
                        "permissions": profile_manager._get_role_permissions(new_role)
                    })
                    st.success(f"✅ Role updated to {new_role} for {all_users[selected_user].get('email')}")
                    st.rerun()
        else:
            st.warning("🔒 Admin access required to view this section.")

# Helper functions for integration with main app
def log_prediction_activity(user_id: str, prediction_result: str, disaster_type: str):
    """Log a prediction activity."""
    profile_manager = UserProfileManager()
    profile_manager.log_activity(
        user_id,
        "prediction_made",
        {
            "result": prediction_result,
            "disaster_type": disaster_type
        }
    )
    profile_manager.increment_stat(user_id, "predictions_made")

def log_resource_allocation(user_id: str, allocation_details: Dict):
    """Log a resource allocation activity."""
    profile_manager = UserProfileManager()
    profile_manager.log_activity(
        user_id,
        "resource_allocation",
        allocation_details
    )
    profile_manager.increment_stat(user_id, "resources_allocated")

def log_bulk_processing(user_id: str, disaster_count: int):
    """Log bulk processing activity."""
    profile_manager = UserProfileManager()
    profile_manager.log_activity(
        user_id,
        "bulk_processing",
        {"disasters_processed": disaster_count}
    )
    profile_manager.increment_stat(user_id, "disasters_processed", disaster_count)

def check_user_permission(permission: str) -> bool:
    """Check if current user has specific permission."""
    if 'user' not in st.session_state:
        return False
    
    user_id = st.session_state.user.get('id')
    profile_manager = UserProfileManager()
    return profile_manager.has_permission(user_id, permission)

if __name__ == "__main__":
    # Test interface
    create_profile_interface()