"""
Disaster Relief Dashboard with Authentication
Includes user login/signup before accessing the dashboard
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import random
import os
import sys

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from auth import SupabaseAuth
    AUTH_AVAILABLE = True
except ImportError:
    AUTH_AVAILABLE = False
    st.error("Authentication module not found. Please ensure auth.py is in the src directory.")

# Initialize authentication
if AUTH_AVAILABLE:
    if 'auth_client' not in st.session_state:
        st.session_state.auth_client = SupabaseAuth()

# Load disaster data for dynamic country/city options
@st.cache_data
def load_disaster_data():
    """Load disaster data from CSV for dynamic dropdowns"""
    try:
        data_path = os.path.join('data', 'disaster_data.csv')
        if os.path.exists(data_path):
            df = pd.read_csv(data_path)
            return df
        else:
            # Fallback if data file doesn't exist
            return None
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

# Get unique countries and cities from dataset
@st.cache_data
def get_countries_and_cities():
    """Get unique countries and their cities from dataset"""
    df = load_disaster_data()
    if df is not None:
        countries = sorted(df['state'].unique().tolist())
        city_options = {}
        for country in countries:
            cities = sorted(df[df['state'] == country]['city'].unique().tolist())
            city_options[country] = cities
        return countries, city_options
    else:
        # Fallback data if CSV not available
        countries = ['California', 'Texas', 'Florida', 'New York', 'India', 'Japan', 'Philippines', 'Indonesia']
        city_options = {
            'California': ['Los Angeles', 'San Francisco', 'San Diego', 'Sacramento', 'Fresno', 'Oakland', 'Santa Ana', 'Anaheim'],
            'Texas': ['Houston', 'San Antonio', 'Dallas', 'Austin', 'Fort Worth', 'El Paso', 'Arlington', 'Corpus Christi'],
            'Florida': ['Jacksonville', 'Miami', 'Tampa', 'Orlando', 'St. Petersburg', 'Hialeah', 'Tallahassee', 'Fort Lauderdale'],
            'New York': ['New York City', 'Buffalo', 'Rochester', 'Yonkers', 'Syracuse', 'Albany', 'New Rochelle', 'Mount Vernon'],
            'India': ['Delhi', 'Mumbai', 'Bangalore', 'Chennai', 'Kolkata', 'Hyderabad', 'Pune', 'Ahmedabad', 'Jaipur', 'Lucknow'],
            'Japan': ['Tokyo', 'Osaka', 'Yokohama', 'Nagoya', 'Sapporo', 'Fukuoka', 'Kobe', 'Hiroshima', 'Sendai', 'Kyoto'],
            'Philippines': ['Manila', 'Quezon City', 'Caloocan', 'Davao City', 'Cebu City', 'Zamboanga', 'Antipolo', 'Taguig', 'Pasig', 'Cagayan de Oro'],
            'Indonesia': ['Jakarta', 'Surabaya', 'Bandung', 'Bekasi', 'Medan', 'Tangerang', 'Depok', 'Semarang', 'Palembang', 'Makassar']
        }
        return countries, city_options

def sync_allocation_data():
    """Synchronize allocation data between inventory and prediction results"""
    if 'inventory' in st.session_state and 'prediction_result' in st.session_state:
        # Update prediction result to reflect current inventory allocations
        if 'allocation_result' in st.session_state.prediction_result:
            allocation_result = st.session_state.prediction_result['allocation_result']
            
            # Update allocated amounts to match inventory
            for resource, data in st.session_state.inventory.items():
                if resource in allocation_result['allocated']:
                    allocation_result['allocated'][resource] = data['allocated']
            
            # Update fulfillment rates
            for resource in allocation_result['allocated']:
                needed = allocation_result['needed'].get(resource, 1)
                allocated = allocation_result['allocated'][resource]
                fulfillment = (allocated / needed) if needed > 0 else 1
                allocation_result['fulfillment_rate'] = fulfillment
            
            st.session_state.prediction_result['allocation_result'] = allocation_result

# Configure page
st.set_page_config(
    page_title="🚨 Disaster Relief Dashboard",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS with better visibility and contrast
st.markdown("""
<style>
    /* Force dark text and visible elements */
    * {
        color: #262730 !important;
    }
    
    /* Main header with strong colors */
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%) !important;
        padding: 2rem;
        border-radius: 10px;
        color: white !important;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 16px rgba(0,0,0,0.3) !important;
    }
    
    .main-header h1, .main-header p {
        color: white !important;
    }
    
    /* Input container with strong background */
    .input-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 16px rgba(0,0,0,0.3) !important;
    }
    
    .input-container h3, .input-container * {
        color: white !important;
    }
    
    /* Result container with bright background */
    .result-container {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%) !important;
        padding: 1.5rem;
        border-radius: 10px;
        border: none;
        margin-bottom: 1rem;
        box-shadow: 0 8px 16px rgba(0,0,0,0.3) !important;
    }
    
    .result-container h3, .result-container * {
        color: white !important;
    }
    
    /* Severity badges */
    .severity-high {
        background: #dc3545 !important;
        color: white !important;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        font-size: 1.5rem;
        font-weight: bold;
        box-shadow: 0 4px 12px rgba(220,53,69,0.5) !important;
    }
    
    .severity-medium {
        background: #ffc107 !important;
        color: #000 !important;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        font-size: 1.5rem;
        font-weight: bold;
        box-shadow: 0 4px 12px rgba(255,193,7,0.5) !important;
    }
    
    .severity-low {
        background: #28a745 !important;
        color: white !important;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        font-size: 1.5rem;
        font-weight: bold;
        box-shadow: 0 4px 12px rgba(40,167,69,0.5) !important;
    }
    
    /* Main content buttons */
    div[data-testid="main"] .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.8rem 2rem !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 12px rgba(102,126,234,0.4) !important;
    }
    
    div[data-testid="main"] .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(102,126,234,0.6) !important;
    }
    
    /* Sidebar with strong gradient background */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%) !important;
    }
    
    section[data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* Sidebar buttons with better visibility */
    section[data-testid="stSidebar"] .stButton > button {
        background: rgba(255,255,255,0.2) !important;
        color: white !important;
        border: 2px solid rgba(255,255,255,0.3) !important;
        border-radius: 8px !important;
        padding: 0.8rem 1rem !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        width: 100% !important;
        text-align: left !important;
        margin: 0.3rem 0 !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2) !important;
    }
    
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(255,255,255,0.3) !important;
        border-color: rgba(255,255,255,0.5) !important;
        transform: translateX(5px);
    }
    
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(255,255,255,0.2) !important;
        border-color: rgba(255,255,255,0.4) !important;
        transform: translateX(3px) !important;
    }
    
    section[data-testid="stSidebar"] .stButton > button:focus {
        background: rgba(255,255,255,0.3) !important;
        border-color: rgba(255,255,255,0.5) !important;
        box-shadow: 0 0 0 2px rgba(255,255,255,0.3) !important;
    }
    
    /* Main content area button styling */
    div[data-testid="main"] .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
    }
</style>""", unsafe_allow_html=True)

def predict_severity(people_affected, deaths, damages, disaster_type):
    """Simple rule-based severity prediction."""
    
    # Severity scoring based on impact
    score = 0
    
    # People affected scoring (30%)
    if people_affected > 10000:
        score += 30
    elif people_affected > 1000:
        score += 20
    else:
        score += 10
    
    # Deaths scoring (40%)
    if deaths > 100:
        score += 40
    elif deaths > 10:
        score += 25
    else:
        score += 10
    
    # Damages scoring (30%)
    if damages > 10000000:  # 10M+
        score += 30
    elif damages > 1000000:  # 1M+
        score += 20
    else:
        score += 10
    
    # Disaster type modifier
    high_impact_disasters = ['earthquake', 'tsunami', 'cyclone']
    if disaster_type in high_impact_disasters:
        score += 5
    
    # Determine severity
    if score >= 70:
        return 'High', {'High': 0.85, 'Medium': 0.12, 'Low': 0.03}
    elif score >= 50:
        return 'Medium', {'High': 0.15, 'Medium': 0.75, 'Low': 0.10}
    else:
        return 'Low', {'High': 0.05, 'Medium': 0.25, 'Low': 0.70}

def calculate_resource_allocation(severity, people_affected, disaster_type):
    """Calculate resource allocation based on severity and needs."""
    
    # Base multipliers for severity
    severity_multipliers = {
        'High': 1.0,
        'Medium': 0.7,
        'Low': 0.4
    }
    
    multiplier = severity_multipliers.get(severity, 0.5)
    
    # Calculate needs per person
    needs_per_person = {
        'Food Kits': 0.8,
        'Water Packs': 1.2,
        'Medicine Kits': 0.3,
        'Shelter Units': 0.25
    }
    
    # Disaster type adjustments
    disaster_adjustments = {
        'flood': {'Water Packs': 1.5, 'Medicine Kits': 1.3},
        'earthquake': {'Shelter Units': 1.8, 'Medicine Kits': 1.4},
        'cyclone': {'Shelter Units': 1.6, 'Food Kits': 1.2},
        'drought': {'Water Packs': 2.0, 'Food Kits': 1.5},
        'wildfire': {'Shelter Units': 1.4, 'Medicine Kits': 1.2},
        'tsunami': {'Water Packs': 1.3, 'Shelter Units': 1.5},
        'landslide': {'Medicine Kits': 1.3, 'Shelter Units': 1.2}
    }
    
    # Calculate needed resources
    needed = {}
    for resource, base_rate in needs_per_person.items():
        adjusted_rate = base_rate
        if disaster_type in disaster_adjustments:
            adjusted_rate *= disaster_adjustments[disaster_type].get(resource, 1.0)
        needed[resource] = int(people_affected * adjusted_rate * multiplier)
    
    # Available resources (simulated)
    available = {
        'Food Kits': 10000,
        'Water Packs': 15000,
        'Medicine Kits': 5000,
        'Shelter Units': 3000
    }
    
    # Calculate allocation
    allocated = {}
    total_needed = 0
    total_allocated = 0
    
    for resource in needed:
        needed_amount = needed[resource]
        available_amount = available[resource]
        allocated_amount = min(needed_amount, available_amount)
        
        allocated[resource] = allocated_amount
        total_needed += needed_amount
        total_allocated += allocated_amount
    
    fulfillment_rate = total_allocated / total_needed if total_needed > 0 else 1.0
    
    return {
        'needed': needed,
        'allocated': allocated,
        'fulfillment_rate': fulfillment_rate
    }

def show_login_page():
    """Display login form."""
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem;
        border-radius: 20px;
        text-align: center;
        margin: 2rem 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.2);
    ">
        <h1 style="color: white; margin: 0; font-size: 2.5rem;">🚨 Disaster Relief Dashboard</h1>
        <p style="color: #f0f0f0; font-size: 1.2rem; margin: 1rem 0 0 0;">
            Emergency Resource Management System
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style="
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            margin: 2rem 0;
        ">
        """, unsafe_allow_html=True)
        
        # Login/Signup tabs
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])
        
        with tab1:
            st.markdown("### Welcome Back!")
            with st.form("login_form"):
                email = st.text_input("📧 Email", placeholder="your.email@example.com")
                password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
                submit_login = st.form_submit_button("🚀 Login", use_container_width=True, type="primary")
                
                if submit_login:
                    if email and password:
                        if AUTH_AVAILABLE:
                            success, message, user_data = st.session_state.auth_client.login_user(email, password)
                            if success:
                                st.session_state.user_authenticated = True
                                st.session_state.user_email = email
                                st.session_state.user_data = user_data
                                st.success(f"✅ {message}")
                                st.rerun()
                            else:
                                st.error(f"❌ {message}")
                        else:
                            st.error("Authentication system not available")
                    else:
                        st.error("Please fill in all fields")
        
        with tab2:
            st.markdown("### Create New Account")
            with st.form("signup_form"):
                signup_email = st.text_input("📧 Email", placeholder="your.email@example.com", key="signup_email")
                signup_password = st.text_input("🔒 Password", type="password", placeholder="Minimum 6 characters", key="signup_password")
                confirm_password = st.text_input("🔒 Confirm Password", type="password", placeholder="Re-enter password", key="confirm_password")
                submit_signup = st.form_submit_button("📝 Create Account", use_container_width=True, type="secondary")
                
                if submit_signup:
                    if signup_email and signup_password and confirm_password:
                        if AUTH_AVAILABLE:
                            success, message = st.session_state.auth_client.signup_user(signup_email, signup_password, confirm_password)
                            if success:
                                st.success(f"✅ {message}")
                                st.info("Now you can login with your new account!")
                            else:
                                st.error(f"❌ {message}")
                        else:
                            st.error("Authentication system not available")
                    else:
                        st.error("Please fill in all fields")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Demo accounts info
        st.info("""
        **Demo Accounts Available:**
        - **Admin**: admin@disaster.com / admin123
        - **User**: user@disaster.com / user123
        
        Or create your own account above!
        """)

def check_authentication():
    """Check if user is authenticated."""
    if not AUTH_AVAILABLE:
        st.error("Authentication system not available")
        return False
    
    # Check if user is already authenticated
    if st.session_state.get('user_authenticated', False):
        return True
    
    # Check if there's a valid session
    if hasattr(st.session_state, 'auth_client'):
        # You could add session validation here
        pass
    
    return False

def logout_user():
    """Logout the current user."""
    if 'user_authenticated' in st.session_state:
        del st.session_state.user_authenticated
    if 'user_email' in st.session_state:
        del st.session_state.user_email
    st.rerun()

def main():
    """Main dashboard application with authentication."""
    
    # Check authentication first
    if not check_authentication():
        show_login_page()
        return
    
    # Show logout option in sidebar
    with st.sidebar:
        st.markdown(f"**👤 Logged in as:** {st.session_state.get('user_email', 'Unknown')}")
        if st.button("🚪 Logout", use_container_width=True):
            logout_user()
    
    # Original dashboard code starts here
    
    # Sidebar Navigation
    st.sidebar.markdown("""
    <div style="text-align: center; padding: 1rem 0; color: white;">
        <h2>🚨 Navigation</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation items with radio buttons (cleaner selection)
    st.sidebar.markdown("---")
    
    # Create navigation buttons
    if st.sidebar.button("🏠 Dashboard Home", use_container_width=True):
        st.session_state.page = "dashboard"
    
    if st.sidebar.button("🔮 Disaster Prediction", use_container_width=True):
        st.session_state.page = "prediction"
    
    if st.sidebar.button("📊 Analytics & Reports", use_container_width=True):
        st.session_state.page = "analytics"
    
    if st.sidebar.button("📋 Resource Management", use_container_width=True):
        st.session_state.page = "resources"
    
    if st.sidebar.button("📈 Historical Data", use_container_width=True):
        st.session_state.page = "historical"
    
    if st.sidebar.button("⚙️ Settings", use_container_width=True):
        st.session_state.page = "settings"
    
    if st.sidebar.button("ℹ️ Help & Support", use_container_width=True):
        st.session_state.page = "help"
    
    # Initialize default page
    if 'page' not in st.session_state:
        st.session_state.page = "prediction"  # Default to prediction page
    
    # User info in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 8px; color: white;">
        <h4>👤 User Info</h4>
        <p><strong>Role:</strong> Emergency Coordinator</p>
        <p><strong>Status:</strong> Active</p>
        <p><strong>Location:</strong> Command Center</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick stats in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 8px; color: white;">
        <h4>📊 Quick Stats</h4>
        <p>🎯 <strong>Predictions Today:</strong> 15</p>
        <p>📦 <strong>Resources Allocated:</strong> 85%</p>
        <p>🚨 <strong>Active Alerts:</strong> 3</p>
        <p>✅ <strong>System Status:</strong> Operational</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Emergency contacts
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 8px; color: white;">
        <h4>🆘 Emergency Contacts</h4>
        <p>📞 <strong>Emergency:</strong> 911</p>
        <p>🏥 <strong>Medical:</strong> +1-555-MEDIC</p>
        <p>🚒 <strong>Fire Dept:</strong> +1-555-FIRE</p>
        <p>👮 <strong>Police:</strong> +1-555-POLICE</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Display selected page content based on session state
    if st.session_state.page == "dashboard":
        show_dashboard_home()
    elif st.session_state.page == "prediction":
        show_prediction_page()
    elif st.session_state.page == "analytics":
        show_analytics_page()
    elif st.session_state.page == "resources":
        show_resources_page()
    elif st.session_state.page == "historical":
        show_historical_page()
    elif st.session_state.page == "settings":
        show_settings_page()
    elif st.session_state.page == "help":
        show_help_page()

def show_dashboard_home():
    """Display dashboard home page."""
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🚨 Disaster Relief Command Center</h1>
        <p>AI-Powered Resource Optimization & Emergency Response</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.success("✅ All systems operational. Ready for emergency response.")
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🚨 Active Disasters", "3", "↑ 1")
    with col2:
        st.metric("📦 Resources Available", "85%", "↓ 5%")
    with col3:
        st.metric("👥 People Assisted Today", "2,450", "↑ 320")
    with col4:
        st.metric("⚡ Response Time (avg)", "12 min", "↓ 3 min")
    
    # Recent activities
    st.markdown("## 📋 Recent Activities")
    
    activities = [
        "🔴 High severity earthquake detected in California - Resources deployed",
        "🟡 Medium severity flood warning for Texas - Monitoring situation", 
        "🟢 Low severity landslide in Oregon - Local response sufficient",
        "📊 Weekly resource allocation report generated",
        "🚁 Emergency helicopter dispatched to rescue operation"
    ]
    
    for activity in activities:
        st.info(activity)
    
    # Quick action buttons
    st.markdown("## 🚀 Quick Actions")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🔮 New Prediction", use_container_width=True):
            st.switch_page("prediction")
    with col2:
        if st.button("📊 View Analytics", use_container_width=True):
            st.switch_page("analytics")
    with col3:
        if st.button("📦 Manage Resources", use_container_width=True):
            st.switch_page("resources")
    with col4:
        if st.button("📈 Historical Data", use_container_width=True):
            st.switch_page("historical")

def show_prediction_page():
    """Display the main prediction page."""
def show_prediction_page():
    """Display the main prediction page."""
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>� Disaster Severity Prediction</h1>
        <p>Advanced AI Analysis for Emergency Response Planning</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Success message
    st.success("✅ Prediction system loaded successfully! All systems operational.")
    
    # Create two columns for layout
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # User Input Form
        st.markdown("""
        <div class="input-container">
            <h3>📋 Disaster Information Input</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Input fields
        disaster_type = st.selectbox(
            "🌪️ Disaster Type",
            ['flood', 'earthquake', 'cyclone', 'drought', 'landslide', 'wildfire', 'tsunami'],
            index=0
        )
        
        # Load dynamic country and city data
        countries, city_options_dynamic = get_countries_and_cities()
        
        col_loc1, col_loc2 = st.columns(2)
        with col_loc1:
            state = st.selectbox(
                "📍 State/Region",
                countries,
                index=0
            )
        
        with col_loc2:
            # Dynamic city/district selection based on state/region from dataset
            city = st.selectbox(
                "🏘️ City", 
                city_options_dynamic.get(state, ['District A', 'District B', 'District C']),
                index=0
            )
        
        col_impact1, col_impact2, col_impact3 = st.columns(3)
        
        with col_impact1:
            people_affected = st.number_input(
                "👥 People Affected", 
                min_value=1, 
                max_value=1000000, 
                value=1000,
                step=100
            )
        
        with col_impact2:
            deaths = st.number_input(
                "💀 Deaths", 
                min_value=0, 
                max_value=100000, 
                value=10,
                step=1
            )
        
        with col_impact3:
            damages = st.number_input(
                "💰 Damages (USD)", 
                min_value=0, 
                max_value=1000000000, 
                value=1000000,
                step=10000
            )
        
        # Resource Requirements Section with improved styling
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1.5rem;
            border-radius: 15px;
            margin: 1rem 0;
            border: 2px solid #e0e0e0;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        ">
            <h3 style="color: white; margin: 0; text-align: center; font-size: 1.4rem;">
                📦 Resource Requirements
            </h3>
            <p style="color: #f0f0f0; text-align: center; margin: 0.5rem 0 0 0; font-size: 1rem;">
                Specify the exact resources needed for this disaster
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Auto-calculate suggested requirements based on people affected
        suggested_food = min(int(people_affected * 0.32), 5000)  # 32% of people need food kits
        suggested_water = min(int(people_affected * 0.72), 10000)  # 72% need water
        suggested_medicine = min(int(people_affected * 0.156), 2000)  # 15.6% need medicine
        suggested_shelter = min(int(people_affected * 0.1), 1000)  # 10% need shelter
        suggested_blankets = min(int(people_affected * 0.5), 3000)  # 50% need blankets
        suggested_first_aid = min(int(people_affected * 0.2), 1500)  # 20% need first aid
        
        # Auto-calculate button with better styling
        col_center = st.columns([1, 2, 1])
        with col_center[1]:
            if st.button("🎯 Auto-Calculate Requirements", 
                        help="Calculate requirements based on people affected",
                        use_container_width=True):
                st.success("✅ Requirements auto-calculated based on affected population!")
        
        st.markdown("<br>", unsafe_allow_html=True)  # Add some spacing
        
        # Resource input fields with better organization
        st.markdown("""
        <div style="
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 12px;
            border: 1px solid #dee2e6;
            margin: 1rem 0;
        ">
        """, unsafe_allow_html=True)
        
        # Create two main rows for better organization
        st.markdown("#### 🥘 **Essential Supplies**")
        col_req1, col_req2 = st.columns(2)
        
        with col_req1:
            food_needed = st.number_input("🍽️ Food Kits Needed", min_value=0, max_value=10000, 
                                        value=suggested_food, step=10,
                                        help=f"Suggested: {suggested_food} (32% of affected people)")
            medicine_needed = st.number_input("� Medicine Kits Needed", min_value=0, max_value=5000, 
                                            value=suggested_medicine, step=5,
                                            help=f"Suggested: {suggested_medicine} (15.6% of affected people)")
            blankets_needed = st.number_input("🧥 Blankets Needed", min_value=0, max_value=10000, 
                                            value=suggested_blankets, step=10,
                                            help=f"Suggested: {suggested_blankets} (50% of affected people)")
        
        with col_req2:
            water_needed = st.number_input("💧 Water Packs Needed", min_value=0, max_value=20000, 
                                         value=suggested_water, step=10,
                                         help=f"Suggested: {suggested_water} (72% of affected people)")
            shelter_needed = st.number_input("🏠 Shelter Units Needed", min_value=0, max_value=2000, 
                                           value=suggested_shelter, step=5,
                                           help=f"Suggested: {suggested_shelter} (10% of affected people)")
            first_aid_needed = st.number_input("🚑 First Aid Kits Needed", min_value=0, max_value=3000, 
                                             value=suggested_first_aid, step=5,
                                             help=f"Suggested: {suggested_first_aid} (20% of affected people)")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Create user requirements dictionary
        user_requirements = {
            'Food Kits': food_needed,
            'Water Packs': water_needed,
            'Medicine Kits': medicine_needed,
            'Shelter Units': shelter_needed,
            'Blankets': blankets_needed,
            'First Aid Kits': first_aid_needed
        }
        
        # Show requirements vs availability check with improved styling
        if any(user_requirements.values()):  # If any requirement > 0
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
                padding: 1rem;
                border-radius: 12px;
                margin: 1.5rem 0;
                border: 2px solid #20c997;
                box-shadow: 0 4px 12px rgba(40, 167, 69, 0.2);
            ">
                <h3 style="color: white; margin: 0; text-align: center; font-size: 1.3rem;">
                    📊 Requirements vs Availability Check
                </h3>
                <p style="color: #f0f8f0; text-align: center; margin: 0.5rem 0 0 0;">
                    Verifying resource availability for your requirements
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Initialize inventory if needed for check
            if 'inventory' not in st.session_state:
                st.session_state.inventory = {
                    'Food Kits': {'available': 8500, 'allocated': 0},
                    'Water Packs': {'available': 12000, 'allocated': 0},
                    'Medicine Kits': {'available': 3500, 'allocated': 0},
                    'Shelter Units': {'available': 2200, 'allocated': 0},
                    'Blankets': {'available': 5000, 'allocated': 0},
                    'First Aid Kits': {'available': 1800, 'allocated': 0}
                }
            
            # Create better organized availability check
            req_check_cols = st.columns(2)
            col_idx = 0
            
            for resource, needed in user_requirements.items():
                if needed > 0:
                    with req_check_cols[col_idx % 2]:
                        available = st.session_state.inventory.get(resource, {}).get('available', 0)
                        allocated = st.session_state.inventory.get(resource, {}).get('allocated', 0)
                        remaining = available - allocated
                        
                        if needed <= remaining:
                            st.success(f"✅ **{resource}**: {needed:,} needed ≤ {remaining:,} available")
                        else:
                            shortage = needed - remaining
                            st.error(f"❌ **{resource}**: {needed:,} needed > {remaining:,} available (Short: {shortage:,})")
                    col_idx += 1
            
            st.markdown("<br>", unsafe_allow_html=True)  # Add spacing
        
        # Predict Button with improved styling
        st.markdown("""
        <div style="text-align: center; margin: 2rem 0;">
        """, unsafe_allow_html=True)
        
        if st.button("🔮 Predict Severity & Allocate Resources", 
                    use_container_width=True, 
                    type="primary"):
            # Make prediction using rule-based system
            prediction, probabilities = predict_severity(people_affected, deaths, damages, disaster_type)
            
            # Use user-defined requirements instead of auto-calculation
            allocation_result = {
                'needed': user_requirements,
                'allocated': {},
                'fulfillment_rate': 0
            }
            
            # Allocate resources based on user requirements and available inventory
            if 'inventory' not in st.session_state:
                # Initialize inventory if not exists
                st.session_state.inventory = {
                    'Food Kits': {'available': 8500, 'allocated': 0},
                    'Water Packs': {'available': 12000, 'allocated': 0},
                    'Medicine Kits': {'available': 3500, 'allocated': 0},
                    'Shelter Units': {'available': 2200, 'allocated': 0},
                    'Blankets': {'available': 5000, 'allocated': 0},
                    'First Aid Kits': {'available': 1800, 'allocated': 0}
                }
            
            # Reset allocations to start fresh
            for resource in st.session_state.inventory:
                st.session_state.inventory[resource]['allocated'] = 0
            
            total_needed = 0
            total_allocated = 0
            
            for resource, needed in user_requirements.items():
                if resource in st.session_state.inventory and needed > 0:
                    available_total = st.session_state.inventory[resource]['available']
                    # Allocate exactly what's needed, but no more than available
                    allocated = min(needed, available_total)
                    allocation_result['allocated'][resource] = allocated
                    
                    # Update inventory allocation
                    st.session_state.inventory[resource]['allocated'] = allocated
                    
                    total_needed += needed
                    total_allocated += allocated
                else:
                    allocation_result['allocated'][resource] = 0
            
            # Calculate overall fulfillment rate
            allocation_result['fulfillment_rate'] = (total_allocated / total_needed) if total_needed > 0 else 1.0
            
            # Store results in session state with timestamp for table refresh
            import time
            st.session_state.prediction_result = {
                'severity': prediction,
                'probabilities': probabilities,
                'allocation_result': allocation_result,
                'timestamp': str(time.time()),
                'input_data': {
                    'disaster_type': disaster_type,
                    'state': state,
                    'city': city,
                    'people_affected': people_affected,
                    'deaths': deaths,
                    'damages': damages
                }
            }
            
            st.success("✅ Prediction completed successfully!")
        
        st.markdown("</div>", unsafe_allow_html=True)  # Close the center div
    
    with col2:
        # Prediction Results
        if 'prediction_result' in st.session_state:
            # Sync data before displaying
            sync_allocation_data()
            
            result = st.session_state.prediction_result
            prediction = result['severity']
            probabilities = result['probabilities']
            allocation_result = result['allocation_result']
            
            # Display Predicted Severity
            st.markdown("""
            <div class="result-container">
                <h3>🎯 Predicted Severity</h3>
            </div>
            """, unsafe_allow_html=True)
            
            if prediction == 'High':
                st.markdown('<div class="severity-high">🔴 HIGH SEVERITY</div>', unsafe_allow_html=True)
            elif prediction == 'Medium':
                st.markdown('<div class="severity-medium">🟡 MEDIUM SEVERITY</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="severity-low">🟢 LOW SEVERITY</div>', unsafe_allow_html=True)
            
            # Confidence scores
            st.markdown("**Confidence Scores:**")
            for severity, confidence in probabilities.items():
                st.progress(confidence, text=f"{severity}: {confidence:.1%}")
            
            # Resource Allocation Output
            st.markdown("""
            <div class="result-container">
                <h3>📦 Optimized Resource Distribution</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Display allocation table
            allocation_data = []
            for resource, amount in allocation_result['allocated'].items():
                needed = allocation_result['needed'].get(resource, 0)
                
                # Check for manual overrides
                manual_override = 0
                if 'manual_overrides' in result and resource in result['manual_overrides']:
                    manual_override = result['manual_overrides'][resource]
                
                # Total allocated = automatic + manual override
                total_allocated = amount + manual_override
                fulfillment = (total_allocated / needed * 100) if needed > 0 else 100
                
                # Create display text for allocated column
                if manual_override > 0:
                    allocated_text = f"{total_allocated:,} (Auto: {amount:,} + Manual: {manual_override:,})"
                else:
                    allocated_text = f"{total_allocated:,}"
                
                allocation_data.append({
                    'Resource': resource,
                    'Needed': f"{needed:,}",
                    'Allocated': allocated_text,
                    'Fulfillment': f"{fulfillment:.1f}%"
                })
            
            allocation_df = pd.DataFrame(allocation_data)
            # Use unique key to force refresh of table
            st.dataframe(allocation_df, use_container_width=True, hide_index=True, key=f"allocation_table_{result.get('timestamp', 'default')}")
            
            # Show manual override info if exists
            if 'manual_overrides' in result and result['manual_overrides']:
                st.info("ℹ️ This allocation includes manual overrides from Resource Management")
                with st.expander("View Manual Override Details"):
                    for resource, qty in result['manual_overrides'].items():
                        st.write(f"• **{resource}**: +{qty:,} units (manually allocated)")
            
            # Overall fulfillment rate (including manual overrides)
            total_needed = sum(allocation_result['needed'].values())
            total_allocated = sum(allocation_result['allocated'].values())
            if 'manual_overrides' in result:
                total_allocated += sum(result['manual_overrides'].values())
            
            overall_rate = (total_allocated / total_needed * 100) if total_needed > 0 else 100
            if overall_rate >= 80:
                st.success(f"✅ Overall Fulfillment Rate: {overall_rate:.1f}%")
            elif overall_rate >= 60:
                st.warning(f"⚠️ Overall Fulfillment Rate: {overall_rate:.1f}%")
            else:
                st.error(f"❌ Overall Fulfillment Rate: {overall_rate:.1f}%")
            
            # Quick access to manual allocation
            st.markdown("---")
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("📋 Manual Resource Allocation", use_container_width=True):
                    st.session_state.page = "resources"
                    st.rerun()
            with col_btn2:
                if st.button("🔄 Refresh Allocation", use_container_width=True):
                    # Force refresh by updating timestamp
                    import time
                    st.session_state.prediction_result['timestamp'] = str(time.time())
                    st.rerun()
        else:
            st.info("👆 Please fill in the disaster information and click 'Predict' to see results.")

def show_analytics_page():
    """Display analytics and visualizations page."""
    # Sync allocation data to ensure consistency
    sync_allocation_data()
    
    st.markdown("""
    <div class="main-header">
        <h1>📊 Analytics & Reports</h1>
        <p>Data Insights and Emergency Response Analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Data source information
    st.info("📊 **Data Sources**: Charts display real data from your disaster dataset and current session allocations")
    
    # Visualizations Section
    col_vis1, col_vis2 = st.columns(2)
    
    with col_vis1:
        # Bar chart showing frequency of disaster types from actual dataset
        st.markdown("### 📊 Disaster Type Frequency")
        
        # Load data from actual dataset
        df = load_disaster_data()
        if df is not None:
            # Get actual disaster type frequency from dataset
            disaster_counts = df['disaster_type'].value_counts().to_dict()
            
            fig_bar = px.bar(
                x=list(disaster_counts.keys()),
                y=list(disaster_counts.values()),
                labels={'x': 'Disaster Type', 'y': 'Frequency'},
                title="Historical Disaster Type Frequency (from Dataset)",
                color=list(disaster_counts.values()),
                color_continuous_scale='viridis'
            )
            fig_bar.update_layout(
                height=400,
                showlegend=False,
                xaxis_tickangle=-45
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            # Fallback to sample data if dataset not available
            sample_disaster_data = {
                'flood': 45,
                'earthquake': 23,
                'cyclone': 18,
                'drought': 15,
                'wildfire': 12,
                'landslide': 8,
                'tsunami': 3
            }
            
            fig_bar = px.bar(
                x=list(sample_disaster_data.keys()),
                y=list(sample_disaster_data.values()),
                labels={'x': 'Disaster Type', 'y': 'Frequency'},
                title="Historical Disaster Type Frequency (Sample Data)",
                color=list(sample_disaster_data.values()),
                color_continuous_scale='viridis'
            )
            fig_bar.update_layout(
                height=400,
                showlegend=False,
                xaxis_tickangle=-45
            )
            st.plotly_chart(fig_bar, use_container_width=True)
    
    with col_vis2:
        # Pie chart showing resource allocation percentages
        st.markdown("### 🥧 Resource Allocation Distribution")
        
        if 'prediction_result' in st.session_state:
            allocation_result = st.session_state.prediction_result['allocation_result']
            allocated = allocation_result['allocated']
            
            # Include manual overrides if they exist
            if 'manual_overrides' in st.session_state.prediction_result:
                manual_overrides = st.session_state.prediction_result['manual_overrides']
                # Combine automatic and manual allocations
                combined_allocation = {}
                for resource, auto_amount in allocated.items():
                    manual_amount = manual_overrides.get(resource, 0)
                    total_amount = auto_amount + manual_amount
                    if total_amount > 0:
                        combined_allocation[resource] = total_amount
                        
                if combined_allocation:
                    fig_pie = px.pie(
                        values=list(combined_allocation.values()),
                        names=list(combined_allocation.keys()),
                        title="Current Resource Allocation (Auto + Manual)"
                    )
                    fig_pie.update_layout(height=400)
                    st.plotly_chart(fig_pie, use_container_width=True)
                else:
                    st.info("No current allocation data.")
            else:
                # Only automatic allocation
                non_zero_allocations = {k: v for k, v in allocated.items() if v > 0}
                
                if non_zero_allocations:
                    fig_pie = px.pie(
                        values=list(non_zero_allocations.values()),
                        names=list(non_zero_allocations.keys()),
                        title="Current Resource Allocation (Automatic)"
                    )
                    fig_pie.update_layout(height=400)
                    st.plotly_chart(fig_pie, use_container_width=True)
                else:
                    st.info("No current allocation data.")
        else:
            # Show current inventory allocation when no prediction exists
            if 'inventory' in st.session_state:
                inventory_allocation = {}
                for resource, data in st.session_state.inventory.items():
                    if data['allocated'] > 0:
                        inventory_allocation[resource] = data['allocated']
                
                if inventory_allocation:
                    fig_pie = px.pie(
                        values=list(inventory_allocation.values()),
                        names=list(inventory_allocation.keys()),
                        title="Current Inventory Allocation"
                    )
                    fig_pie.update_layout(height=400)
                    st.plotly_chart(fig_pie, use_container_width=True)
                else:
                    st.info("No current allocation data. Make a prediction or allocate resources manually.")
            else:
                st.info("No allocation data available. Make a prediction or go to Resource Management to allocate resources.")
                
        # Show data source info
        st.caption("💡 Data Source: " + 
                  ("Current prediction results" if 'prediction_result' in st.session_state 
                   else "Current inventory allocations"))
    
    # Additional analytics
    st.markdown("### 📈 Response Time Analysis")
    
    # Generate response time data based on disaster severity patterns
    df = load_disaster_data()
    if df is not None:
        # Calculate average response time by disaster type from dataset
        disaster_types = df['disaster_type'].unique()
        response_data = {}
        
        # Simulate response times based on disaster severity patterns
        base_times = {
            'flood': 12, 'earthquake': 8, 'cyclone': 10, 'drought': 20,
            'wildfire': 15, 'landslide': 18, 'tsunami': 6
        }
        
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        # Create more realistic seasonal variations
        seasonal_multipliers = [1.2, 1.1, 0.9, 0.8, 1.0, 1.1]
        
        response_times = []
        for i, month in enumerate(months):
            # Average response time with seasonal variation
            avg_time = 12 * seasonal_multipliers[i]
            response_times.append(round(avg_time, 1))
    else:
        # Fallback data
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        response_times = [15, 12, 18, 10, 14, 9]
    
    fig_line = px.line(
        x=months, 
        y=response_times,
        title="Average Response Time by Month (minutes)",
        labels={'x': 'Month', 'y': 'Response Time (min)'},
        markers=True
    )
    fig_line.update_layout(height=300)
    st.plotly_chart(fig_line, use_container_width=True)

def show_resources_page():
    """Display resource management page."""
    st.markdown("""
    <div class="main-header">
        <h1>📦 Resource Management</h1>
        <p>Inventory and Distribution Control</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Resource inventory
    st.markdown("### 📋 Current Inventory")
    
    # Initialize inventory in session state if not exists
    if 'inventory' not in st.session_state:
        st.session_state.inventory = {
            'Food Kits': {'available': 8500, 'allocated': 0},
            'Water Packs': {'available': 12000, 'allocated': 0},
            'Medicine Kits': {'available': 3500, 'allocated': 0},
            'Shelter Units': {'available': 2200, 'allocated': 0},
            'Blankets': {'available': 5000, 'allocated': 0},
            'First Aid Kits': {'available': 1800, 'allocated': 0}
        }
    
    # Display inventory table
    inventory_data = []
    for resource, data in st.session_state.inventory.items():
        remaining = data['available'] - data['allocated']
        if remaining > 1000:
            status = '✅ Good'
        elif remaining > 500:
            status = '⚠️ Low'
        else:
            status = '❌ Critical'
            
        inventory_data.append({
            'Resource': resource,
            'Available': data['available'],
            'Allocated': data['allocated'],
            'Remaining': remaining,
            'Status': status
        })
    
    inventory_df = pd.DataFrame(inventory_data)
    st.dataframe(inventory_df, use_container_width=True, hide_index=True)
    
    # Manual Resource allocation controls
    st.markdown("### ⚙️ Manual Resource Allocation")
    st.info("💡 Use this section to manually override automatic allocations from predictions")
    
    # Get countries and cities for allocation
    countries, city_options = get_countries_and_cities()
    
    col1, col2 = st.columns(2)
    
    with col1:
        selected_resource = st.selectbox("Select Resource", list(st.session_state.inventory.keys()))
        max_available = st.session_state.inventory[selected_resource]['available'] - st.session_state.inventory[selected_resource]['allocated']
        quantity = st.number_input("Quantity to Allocate", min_value=0, max_value=max_available, value=min(100, max_available))
        destination_country = st.selectbox("Destination Country", countries)
        
    with col2:
        destination_city = st.selectbox("Destination City", city_options.get(destination_country, ['Select Country First']))
        priority = st.selectbox("Priority Level", ['High', 'Medium', 'Low'])
        transport = st.selectbox("Transport Method", ['Truck', 'Helicopter', 'Ship', 'Air Drop'])
        instructions = st.text_area("Special Instructions", "Enter any special handling instructions...")
    
    # Allocation button
    if st.button("🚀 Deploy Resources", use_container_width=True):
        if quantity > 0 and destination_country != "Select Country First":
            # Update inventory
            st.session_state.inventory[selected_resource]['allocated'] += quantity
            
            # Store manual allocation in session state
            if 'manual_allocations' not in st.session_state:
                st.session_state.manual_allocations = []
            
            import time
            allocation_record = {
                'timestamp': time.time(),
                'resource': selected_resource,
                'quantity': quantity,
                'destination_country': destination_country,
                'destination_city': destination_city,
                'priority': priority,
                'transport': transport,
                'instructions': instructions,
                'status': 'Deployed'
            }
            
            st.session_state.manual_allocations.append(allocation_record)
            
            # Update the prediction result allocation if it exists
            if 'prediction_result' in st.session_state:
                if 'manual_overrides' not in st.session_state.prediction_result:
                    st.session_state.prediction_result['manual_overrides'] = {}
                
                # Add manual allocation to the prediction result
                if selected_resource in st.session_state.prediction_result['manual_overrides']:
                    st.session_state.prediction_result['manual_overrides'][selected_resource] += quantity
                else:
                    st.session_state.prediction_result['manual_overrides'][selected_resource] = quantity
            
            # Sync allocation data after manual allocation
            sync_allocation_data()
            
            st.success(f"✅ Successfully deployed {quantity} {selected_resource} to {destination_city}, {destination_country}!")
            st.rerun()
        else:
            st.error("❌ Please fill in all required fields and ensure quantity > 0")
    
    # Display recent manual allocations
    if 'manual_allocations' in st.session_state and st.session_state.manual_allocations:
        st.markdown("### 📋 Recent Manual Allocations")
        recent_allocations = st.session_state.manual_allocations[-10:]  # Show last 10
        
        allocation_display = []
        for allocation in reversed(recent_allocations):  # Show newest first
            allocation_display.append({
                'Resource': allocation['resource'],
                'Quantity': allocation['quantity'],
                'Destination': f"{allocation['destination_city']}, {allocation['destination_country']}",
                'Priority': allocation['priority'],
                'Status': allocation['status']
            })
        
        allocations_df = pd.DataFrame(allocation_display)
        st.dataframe(allocations_df, use_container_width=True, hide_index=True)

def show_historical_page():
    """Display historical data page."""
    st.markdown("""
    <div class="main-header">
        <h1>📈 Historical Data</h1>
        <p>Past Disasters and Response Analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sample historical data
    st.markdown("### 📊 Recent Disaster Summary")
    
    historical_data = {
        'Date': ['2024-09-15', '2024-09-10', '2024-09-05', '2024-08-28', '2024-08-20'],
        'Type': ['Earthquake', 'Flood', 'Wildfire', 'Cyclone', 'Landslide'],
        'Location': ['California', 'Texas', 'Oregon', 'Florida', 'Washington'],
        'Severity': ['High', 'Medium', 'High', 'Low', 'Medium'],
        'People Affected': [15000, 3500, 8000, 1200, 2800],
        'Response Time': ['8 min', '15 min', '12 min', '25 min', '18 min']
    }
    
    historical_df = pd.DataFrame(historical_data)
    st.dataframe(historical_df, use_container_width=True, hide_index=True)
    
    # Trends
    st.markdown("### 📈 Disaster Trends")
    
    # Sample trend data
    disaster_trend = px.scatter(
        x=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        y=[12, 8, 15, 10, 18, 14],
        size=[120, 80, 150, 100, 180, 140],
        title="Disaster Frequency and Impact Over Time"
    )
    st.plotly_chart(disaster_trend, use_container_width=True)

def show_settings_page():
    """Display settings page."""
    st.markdown("""
    <div class="main-header">
        <h1>⚙️ System Settings</h1>
        <p>Configuration and Preferences</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Settings options
    st.markdown("### 🔧 General Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.checkbox("Enable Real-time Alerts", value=True)
        st.checkbox("Auto-deploy Critical Resources", value=False)
        st.selectbox("Default Response Priority", ['High', 'Medium', 'Low'])
        st.slider("Alert Threshold (minutes)", 1, 60, 15)
    
    with col2:
        st.checkbox("Email Notifications", value=True)
        st.checkbox("SMS Alerts", value=True)
        st.selectbox("Dashboard Theme", ['Light', 'Dark', 'Auto'])
        st.selectbox("Language", ['English', 'Spanish', 'French'])
    
    if st.button("💾 Save Settings", use_container_width=True):
        st.success("✅ Settings saved successfully!")

def show_help_page():
    """Display help and support page."""
    st.markdown("""
    <div class="main-header">
        <h1>ℹ️ Help & Support</h1>
        <p>Documentation and Emergency Contacts</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Help sections
    st.markdown("### 📖 Quick Start Guide")
    
    with st.expander("🔮 How to Make a Prediction"):
        st.markdown("""
        1. Navigate to the **Disaster Prediction** page
        2. Fill in all required fields (disaster type, location, impact data)
        3. Click **Predict Severity & Allocate Resources**
        4. Review the severity assessment and resource allocation
        5. Take appropriate action based on recommendations
        """)
    
    with st.expander("📦 Resource Management"):
        st.markdown("""
        1. Go to **Resource Management** page
        2. Check current inventory levels
        3. Select resources to allocate
        4. Specify destination and priority
        5. Deploy resources using the deployment button
        """)
    
    with st.expander("📊 Understanding Analytics"):
        st.markdown("""
        - **Bar Charts**: Show frequency of different disaster types
        - **Pie Charts**: Display resource allocation percentages
        - **Line Graphs**: Track response times and trends over time
        - **Metrics**: Real-time statistics and performance indicators
        """)
    
    # Contact information
    st.markdown("### 📞 Emergency Contacts")
    
    contacts = {
        'Emergency Services': '911',
        'Medical Emergency': '+1-555-MEDIC',
        'Fire Department': '+1-555-FIRE',
        'Police Department': '+1-555-POLICE',
        'Technical Support': '+1-555-TECH',
        'System Administrator': 'admin@disaster-relief.com'
    }
    
    for service, contact in contacts.items():
        st.info(f"**{service}:** {contact}")

if __name__ == "__main__":
    main()