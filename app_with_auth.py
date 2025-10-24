"""
Authentication-enabled Streamlit app for Disaster Relief Resource Optimizer.
Includes user signup, login, and session management with Supabase.
"""

import streamlit as st
import sys
import os

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from auth import require_authentication, SUPABASE_SQL_SCHEMA

# Import the main app function from app.py
import importlib.util
spec = importlib.util.spec_from_file_location("main_app", "app.py")
main_app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main_app)

# Configure page
st.set_page_config(
    page_title="Disaster Relief Resource Optimizer",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply authentication requirement to the main app
@require_authentication
def authenticated_main():
    """Main application wrapped with authentication."""
    return main_app.main()

def show_setup_instructions():
    """Show Supabase setup instructions."""
    st.title("🚨 Disaster Relief Resource Optimizer")
    st.subheader("Setup Instructions")
    
    st.markdown("""
    ### Welcome to the Disaster Relief Resource Optimizer!
    
    This application uses **Supabase** for user authentication. Follow these steps to set up:
    
    #### Option 1: Use Demo Mode (No Setup Required)
    - The app will run in demo mode with pre-configured test accounts
    - Demo accounts: `admin@disaster.com / admin123` and `user@disaster.com / user123`
    - You can also create new demo accounts
    
    #### Option 2: Connect to Supabase (Full Features)
    1. **Create a Supabase project** at [supabase.com](https://supabase.com)
    2. **Copy the SQL schema** below into your Supabase SQL Editor
    3. **Update credentials** in `src/auth.py`:
       - Replace `YOUR_SUPABASE_PROJECT_URL` with your project URL
       - Replace `YOUR_SUPABASE_ANON_KEY` with your anon key
    
    #### Supabase SQL Schema
    Copy and paste this into your Supabase SQL Editor:
    """)
    
    # Show SQL schema in a code block
    st.code(SUPABASE_SQL_SCHEMA, language='sql')
    
    # Download button for SQL schema
    st.download_button(
        label="📄 Download SQL Schema",
        data=SUPABASE_SQL_SCHEMA,
        file_name="disaster_relief_schema.sql",
        mime="text/sql"
    )
    
    st.markdown("""
    #### Features
    - 🤖 **ML Prediction**: Random Forest model for disaster severity prediction
    - 📊 **Resource Allocation**: Priority-based algorithm for optimal distribution
    - 📈 **Analytics**: Historical data visualizations and insights
    - 👥 **User Management**: Secure authentication and session handling
    - 📁 **Bulk Processing**: Handle multiple disasters simultaneously
    
    #### Getting Started
    Click the button below to start using the application:
    """)
    
    if st.button("🚀 Launch Application", type="primary"):
        st.session_state.show_setup = False
        st.rerun()

def main():
    """Main entry point with setup check."""
    # Check if user wants to see setup instructions
    if st.session_state.get('show_setup', False):  # Changed default to False
        if st.sidebar.button("Skip Setup - Use Demo Mode"):
            st.session_state.show_setup = False
            st.rerun()
        show_setup_instructions()
    else:
        # Show main authenticated app
        authenticated_main()

if __name__ == "__main__":
    main()