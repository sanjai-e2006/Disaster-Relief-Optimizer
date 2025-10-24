"""
Enhanced Dashboard for Disaster Relief Resource Optimizer
Modern, attractive UI with interactive components and real-time metrics
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from auth import require_authentication
from data_preprocessing import DisasterDataPreprocessor
from ml_model import DisasterSeverityModel
from resource_allocator import ResourceAllocator
from user_profile import (
    UserProfileManager, create_profile_interface, 
    log_prediction_activity, log_resource_allocation, 
    log_bulk_processing, check_user_permission
)
import joblib

# Configure page with enhanced layout
st.set_page_config(
    page_title="🚨 Disaster Relief Command Center",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS for modern, attractive UI
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .main {
        font-family: 'Inter', sans-serif;
    }
    
    /* Header Styles */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    }
    
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-subtitle {
        font-size: 1.2rem;
        font-weight: 300;
        opacity: 0.9;
    }
    
    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #667eea;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #2c3e50;
        margin-bottom: 0.2rem;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #7f8c8d;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Status Cards */
    .status-high {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(255,107,107,0.3);
    }
    
    .status-medium {
        background: linear-gradient(135deg, #feca57 0%, #ff9ff3 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(254,202,87,0.3);
    }
    
    .status-low {
        background: linear-gradient(135deg, #48dbfb 0%, #0abde3 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(72,219,251,0.3);
    }
    
    /* Sidebar Enhancements */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Button Styles */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102,126,234,0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102,126,234,0.4);
    }
    
    /* Alert Styles */
    .alert-container {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #e17055;
        margin: 1rem 0;
    }
    
    /* Chart Container */
    .chart-container {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin: 1rem 0;
    }
    
    /* Navigation Pills */
    .nav-pills {
        display: flex;
        background: #f8f9fa;
        border-radius: 10px;
        padding: 0.3rem;
        margin-bottom: 2rem;
    }
    
    .nav-pill {
        flex: 1;
        text-align: center;
        padding: 0.8rem;
        border-radius: 7px;
        cursor: pointer;
        transition: all 0.3s ease;
        font-weight: 500;
    }
    
    .nav-pill.active {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(102,126,234,0.3);
    }
    
    /* Loading Animation */
    .loading {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 200px;
    }
    
    .spinner {
        border: 4px solid #f3f3f3;
        border-top: 4px solid #667eea;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .main-title {
            font-size: 2rem;
        }
        .metric-value {
            font-size: 1.8rem;
        }
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_model_and_preprocessor():
    """Load the trained model and preprocessor."""
    try:
        model_path = 'models/model.pkl'
        preprocessor_path = 'models/preprocessor.pkl'
        
        if not os.path.exists(model_path) or not os.path.exists(preprocessor_path):
            return None, None, "Model files not found. Please run train_model.py first."
        
        # Load model
        model_data = joblib.load(model_path)
        model = DisasterSeverityModel()
        model.model = model_data['model']
        model.feature_names = model_data['feature_names']
        model.feature_importance = model_data['feature_importance']
        model.is_trained = model_data['is_trained']
        
        # Load preprocessor
        preprocessor = joblib.load(preprocessor_path)
        
        return model, preprocessor, None
    except Exception as e:
        return None, None, f"Error loading model: {str(e)}"

@st.cache_data
def load_dataset():
    """Load the disaster dataset for analysis."""
    try:
        df = pd.read_csv('data/disaster_data.csv')
        return df, None
    except Exception as e:
        return None, f"Error loading dataset: {str(e)}"

def create_dashboard_header():
    """Create an attractive dashboard header."""
    st.markdown("""
    <div class="main-header">
        <div class="main-title">🚨 Disaster Relief Command Center</div>
        <div class="main-subtitle">AI-Powered Resource Optimization & Emergency Response</div>
    </div>
    """, unsafe_allow_html=True)

def create_metric_cards(dataset):
    """Create attractive metric cards for key statistics."""
    if dataset is None:
        return
    
    # Calculate key metrics
    total_disasters = len(dataset)
    total_affected = dataset['people_affected'].sum()
    total_deaths = dataset['deaths'].sum()
    avg_damage = dataset['damages'].mean()
    
    # Create preprocessor instance to calculate severity distribution
    preprocessor = DisasterDataPreprocessor()
    df_with_severity = preprocessor.create_severity_labels(dataset.copy())
    severity_counts = df_with_severity['severity'].value_counts()
    
    # Display metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_disasters:,}</div>
            <div class="metric-label">Total Disasters</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_affected:,.0f}</div>
            <div class="metric-label">People Affected</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_deaths:,.0f}</div>
            <div class="metric-label">Total Deaths</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">${avg_damage:,.0f}</div>
            <div class="metric-label">Avg Damage</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Severity distribution
    st.subheader("📊 Severity Distribution")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        high_count = severity_counts.get('High', 0)
        st.markdown(f"""
        <div class="status-high">
            <h3>{high_count}</h3>
            <p>High Severity</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        medium_count = severity_counts.get('Medium', 0)
        st.markdown(f"""
        <div class="status-medium">
            <h3>{medium_count}</h3>
            <p>Medium Severity</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        low_count = severity_counts.get('Low', 0)
        st.markdown(f"""
        <div class="status-low">
            <h3>{low_count}</h3>
            <p>Low Severity</p>
        </div>
        """, unsafe_allow_html=True)

def create_enhanced_charts(dataset):
    """Create enhanced, interactive charts."""
    if dataset is None:
        return
    
    # Disaster Types Sunburst Chart
    st.subheader("🌅 Disaster Types Overview")
    
    disaster_counts = dataset['disaster_type'].value_counts()
    
    fig_sunburst = go.Figure(go.Sunburst(
        labels=list(disaster_counts.index),
        values=list(disaster_counts.values),
        parents=[""] * len(disaster_counts),
        maxdepth=2,
        branchvalues="total"
    ))
    
    fig_sunburst.update_layout(
        title="Disaster Types Distribution",
        font_size=12,
        height=500,
        showlegend=False
    )
    
    st.plotly_chart(fig_sunburst, use_container_width=True)
    
    # Geographic Impact Heatmap
    st.subheader("🗺️ Geographic Impact Analysis")
    
    # Create state-wise aggregation
    state_impact = dataset.groupby('state').agg({
        'people_affected': 'sum',
        'deaths': 'sum',
        'damages': 'sum'
    }).reset_index()
    
    fig_geo = px.treemap(
        state_impact,
        path=['state'],
        values='people_affected',
        color='deaths',
        color_continuous_scale='Reds',
        title="Impact by State (Size: People Affected, Color: Deaths)"
    )
    
    fig_geo.update_layout(height=500)
    st.plotly_chart(fig_geo, use_container_width=True)
    
    # Time Series Analysis
    st.subheader("📈 Disaster Trends Over Time")
    
    yearly_data = dataset.groupby('year').agg({
        'disaster_type': 'count',
        'people_affected': 'sum',
        'deaths': 'sum'
    }).reset_index()
    
    yearly_data.rename(columns={'disaster_type': 'count'}, inplace=True)
    
    # Create subplot with secondary y-axis
    fig_time = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Disaster Frequency', 'Impact Metrics'),
        vertical_spacing=0.1
    )
    
    # Disaster count
    fig_time.add_trace(
        go.Scatter(
            x=yearly_data['year'],
            y=yearly_data['count'],
            mode='lines+markers',
            name='Disaster Count',
            line=dict(color='#667eea', width=3),
            marker=dict(size=8)
        ),
        row=1, col=1
    )
    
    # People affected and deaths
    fig_time.add_trace(
        go.Scatter(
            x=yearly_data['year'],
            y=yearly_data['people_affected'],
            mode='lines+markers',
            name='People Affected',
            line=dict(color='#ff6b6b', width=2),
            yaxis='y2'
        ),
        row=2, col=1
    )
    
    fig_time.add_trace(
        go.Scatter(
            x=yearly_data['year'],
            y=yearly_data['deaths'],
            mode='lines+markers',
            name='Deaths',
            line=dict(color='#feca57', width=2),
            yaxis='y2'
        ),
        row=2, col=1
    )
    
    fig_time.update_layout(
        height=600,
        showlegend=True,
        title_text="Disaster Trends Analysis"
    )
    
    st.plotly_chart(fig_time, use_container_width=True)

def create_prediction_interface(model, preprocessor):
    """Create an enhanced prediction interface."""
    st.subheader("🔮 AI Disaster Severity Prediction")
    
    # Create a more attractive form
    with st.container():
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📍 Disaster Details")
            year = st.selectbox("Year", range(2020, 2031), index=4)  # Default to 2024
            disaster_type = st.selectbox(
                "Disaster Type",
                ['flood', 'earthquake', 'cyclone', 'drought', 'landslide', 'wildfire', 'tsunami'],
                index=0
            )
            state = st.selectbox(
                "State/Region",
                ['California', 'Texas', 'Florida', 'New York', 'India', 'Japan', 'Philippines', 'Indonesia'],
                index=0
            )
            district = st.selectbox(
                "District", 
                ['District A', 'District B', 'District C', 'District D', 'District E'],
                index=0
            )
        
        with col2:
            st.markdown("### 📊 Impact Metrics")
            people_affected = st.number_input(
                "People Affected", 
                min_value=1, 
                max_value=1000000, 
                value=1000,
                step=100
            )
            deaths = st.number_input(
                "Deaths", 
                min_value=0, 
                max_value=100000, 
                value=10,
                step=1
            )
            damages = st.number_input(
                "Damages (USD)", 
                min_value=0, 
                max_value=1000000000, 
                value=1000000,
                step=10000
            )
        
        # Prediction button
        if st.button("🚀 Predict Severity & Allocate Resources", type="primary"):
            # Prepare input data
            input_data = {
                'year': year,
                'disaster_type': disaster_type,
                'state': state,
                'district': district,
                'people_affected': people_affected,
                'deaths': deaths,
                'damages': damages
            }
            
            try:
                # Show loading spinner
                with st.spinner('🤖 AI is analyzing the disaster...'):
                    # Preprocess input
                    processed_input = preprocessor.preprocess_single_input(input_data)
                    
                    # Make prediction
                    prediction = model.predict(processed_input)[0]
                    probabilities = model.predict_proba(processed_input)[0]
                    
                    # Get class names and confidence scores
                    class_names = model.model.classes_
                    confidence_scores = dict(zip(class_names, probabilities))
                    
                    # Log the prediction activity
                    if 'user' in st.session_state:
                        user_id = st.session_state.user.get('id')
                        log_prediction_activity(user_id, prediction, disaster_type)
                
                # Display results
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### 🎯 Prediction Results")
                    
                    # Display severity with appropriate styling
                    if prediction == 'High':
                        st.markdown(f'<div class="status-high"><h2>🔴 {prediction} Severity</h2></div>', unsafe_allow_html=True)
                    elif prediction == 'Medium':
                        st.markdown(f'<div class="status-medium"><h2>🟡 {prediction} Severity</h2></div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="status-low"><h2>🟢 {prediction} Severity</h2></div>', unsafe_allow_html=True)
                    
                    # Confidence scores
                    st.markdown("#### Confidence Scores")
                    for class_name, score in confidence_scores.items():
                        st.progress(score, text=f"{class_name}: {score:.1%}")
                
                with col2:
                    st.markdown("### 📦 Resource Allocation")
                    
                    # Default resource availability
                    available_resources = {
                        'Food Kits': 10000,
                        'Water Packs': 15000,
                        'Medicine Kits': 5000,
                        'Shelter Units': 3000
                    }
                    
                    # Calculate allocation
                    allocator = ResourceAllocator()
                    allocation_result = allocator.allocate_single_disaster(
                        prediction, people_affected, disaster_type, available_resources
                    )
                    
                    if allocation_result:
                        # Log resource allocation
                        if 'user' in st.session_state:
                            user_id = st.session_state.user.get('id')
                            log_resource_allocation(user_id, {
                                "severity": prediction,
                                "people_affected": people_affected,
                                "fulfillment_rate": allocation_result.get('fulfillment_rate', 0)
                            })
                        
                        # Display allocation
                        for resource, amount in allocation_result['allocated'].items():
                            needed = allocation_result['needed'].get(resource, 0)
                            fulfillment = (amount / needed * 100) if needed > 0 else 100
                            
                            st.metric(
                                label=resource,
                                value=f"{amount:,}",
                                delta=f"{fulfillment:.1f}% fulfilled"
                            )
                        
                        # Overall fulfillment rate
                        overall_rate = allocation_result.get('fulfillment_rate', 0) * 100
                        st.success(f"🎯 Overall Fulfillment Rate: {overall_rate:.1f}%")
                        
                        # Create allocation pie chart
                        allocated = allocation_result['allocated']
                        non_zero_allocations = {k: v for k, v in allocated.items() if v > 0}
                        
                        if non_zero_allocations:
                            fig_pie = px.pie(
                                values=list(non_zero_allocations.values()),
                                names=list(non_zero_allocations.keys()),
                                title="Resource Allocation Breakdown",
                                color_discrete_sequence=px.colors.qualitative.Set3
                            )
                            fig_pie.update_layout(height=400)
                            st.plotly_chart(fig_pie, use_container_width=True)
            
            except Exception as e:
                st.error(f"❌ Error during prediction: {str(e)}")
        
        st.markdown('</div>', unsafe_allow_html=True)

@require_authentication
def main():
    """Main dashboard application."""
    # Create header
    create_dashboard_header()
    
    # Load data and models
    model, preprocessor, model_error = load_model_and_preprocessor()
    dataset, data_error = load_dataset()
    
    if model_error:
        st.error(model_error)
        st.info("Please run `python train_model.py` to train the model first.")
        return
    
    if data_error:
        st.error(data_error)
        return
    
    # Sidebar navigation with enhanced styling
    st.sidebar.markdown("## 🧭 Navigation")
    
    # User info in sidebar
    if 'user' in st.session_state:
        user_email = st.session_state.user.get('email', 'Unknown')
        st.sidebar.markdown(f"👤 **Welcome, {user_email.split('@')[0]}!**")
        
        # Initialize profile manager and update login
        profile_manager = UserProfileManager()
        user_id = st.session_state.user.get('id')
        profile = profile_manager.get_profile(user_id)
        
        if not profile:
            profile = profile_manager.create_profile(user_id, user_email)
        
        profile_manager.update_last_login(user_id)
        
        # Show user role and stats
        role = profile.get('role', 'user').title()
        stats = profile.get('stats', {})
        
        st.sidebar.markdown(f"""
        **Role:** {role}  
        **Predictions:** {stats.get('predictions_made', 0)}  
        **Logins:** {stats.get('login_count', 0)}
        """)
        
        st.sidebar.markdown("---")
    
    # Navigation options
    pages = {
        "🏠 Dashboard Overview": "dashboard",
        "🔮 AI Prediction": "prediction", 
        "📊 Data Analytics": "analytics",
        "⚙️ Bulk Processing": "bulk",
        "👤 User Profile": "profile"
    }
    
    # Filter pages based on permissions
    if 'user' in st.session_state:
        if not check_user_permission("bulk_processing"):
            pages.pop("⚙️ Bulk Processing", None)
    
    selected_page = st.sidebar.selectbox("Choose a page:", list(pages.keys()))
    page_key = pages[selected_page]
    
    # Display selected page
    if page_key == "dashboard":
        st.markdown("## 📈 Real-Time Dashboard")
        create_metric_cards(dataset)
        
        # Recent alerts simulation
        st.markdown("### 🚨 Recent Alerts")
        st.markdown("""
        <div class="alert-container">
            <strong>⚠️ High Severity Alert:</strong> Earthquake detected in California - 
            Immediate resource allocation required for 5,000+ affected people.
        </div>
        """, unsafe_allow_html=True)
        
        # Quick stats
        create_enhanced_charts(dataset)
        
    elif page_key == "prediction":
        create_prediction_interface(model, preprocessor)
        
    elif page_key == "analytics":
        st.markdown("## 📊 Advanced Analytics")
        create_enhanced_charts(dataset)
        
        # Feature importance
        st.subheader("🎯 Model Feature Importance")
        if model.feature_importance:
            feature_df = pd.DataFrame(
                list(model.feature_importance.items()),
                columns=['Feature', 'Importance']
            ).sort_values('Importance', ascending=True)
            
            fig_importance = px.bar(
                feature_df,
                x='Importance',
                y='Feature',
                orientation='h',
                title="ML Model Feature Importance",
                color='Importance',
                color_continuous_scale='viridis'
            )
            fig_importance.update_layout(height=400)
            st.plotly_chart(fig_importance, use_container_width=True)
        
    elif page_key == "bulk":
        # Check permissions for bulk processing
        if not check_user_permission("bulk_processing"):
            st.error("🔒 You don't have permission to access bulk processing.")
            st.info("Please contact your administrator to request bulk processing access.")
            return
        
        st.markdown("## ⚙️ Bulk Disaster Processing")
        st.info("📄 Upload a CSV file with multiple disasters for batch processing.")
        
        # File upload
        uploaded_file = st.file_uploader("Choose CSV file", type="csv")
        
        if uploaded_file:
            try:
                bulk_data = pd.read_csv(uploaded_file)
                st.success(f"✅ Loaded {len(bulk_data)} disasters from file")
                
                # Show preview
                st.subheader("📋 Data Preview")
                st.dataframe(bulk_data.head(), use_container_width=True)
                
                if st.button("🚀 Process All Disasters", type="primary"):
                    with st.spinner("🤖 Processing all disasters..."):
                        # Process bulk predictions (simplified)
                        results = []
                        for idx, row in bulk_data.iterrows():
                            try:
                                input_data = row.to_dict()
                                processed_input = preprocessor.preprocess_single_input(input_data)
                                prediction = model.predict(processed_input)[0]
                                
                                results.append({
                                    'Location': f"{row.get('state', 'Unknown')}, {row.get('district', 'Unknown')}",
                                    'Disaster Type': row.get('disaster_type', 'Unknown'),
                                    'People Affected': row.get('people_affected', 0),
                                    'Predicted Severity': prediction
                                })
                            except:
                                continue
                        
                        if results:
                            results_df = pd.DataFrame(results)
                            st.subheader("📊 Bulk Processing Results")
                            st.dataframe(results_df, use_container_width=True)
                            
                            # Log bulk processing
                            if 'user' in st.session_state:
                                user_id = st.session_state.user.get('id')
                                log_bulk_processing(user_id, len(results))
                            
                            # Summary stats
                            severity_summary = results_df['Predicted Severity'].value_counts()
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("High Severity", severity_summary.get('High', 0))
                            with col2:
                                st.metric("Medium Severity", severity_summary.get('Medium', 0))
                            with col3:
                                st.metric("Low Severity", severity_summary.get('Low', 0))
            
            except Exception as e:
                st.error(f"❌ Error processing file: {str(e)}")
    
    elif page_key == "profile":
        create_profile_interface()

if __name__ == "__main__":
    main()