"""
Direct Disaster Relief Resource Optimizer App
Bypasses setup and goes directly to authentication/main app
"""

import streamlit as st
import sys
import os

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from auth import require_authentication

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

if __name__ == "__main__":
    authenticated_main()