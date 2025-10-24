"""
Disaster Relief Resource Optimizer
Main application launcher with enhanced dashboard and authentication
"""

import streamlit as st
import sys
import os

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from auth import require_authentication

# Enhanced page configuration
st.set_page_config(
    page_title="🚨 Disaster Relief Command Center",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern CSS styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .main {
        font-family: 'Inter', sans-serif;
    }
    
    .welcome-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 3rem;
        box-shadow: 0 15px 35px rgba(0,0,0,0.1);
    }
    
    .welcome-title {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .welcome-subtitle {
        font-size: 1.3rem;
        font-weight: 300;
        opacity: 0.9;
        margin-bottom: 2rem;
    }
    
    .feature-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 2rem;
        border-radius: 15px;
        border-left: 6px solid #667eea;
        margin: 1.5rem 0;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.15);
    }
    
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
        display: block;
    }
    
    .feature-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 0.5rem;
    }
    
    .feature-description {
        color: #7f8c8d;
        font-size: 1rem;
        line-height: 1.6;
    }
    
    .stats-container {
        display: flex;
        justify-content: space-around;
        flex-wrap: wrap;
        margin: 2rem 0;
    }
    
    .stat-item {
        text-align: center;
        padding: 1rem;
        margin: 0.5rem;
        background: white;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        min-width: 150px;
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: 700;
        color: #667eea;
        display: block;
    }
    
    .stat-label {
        font-size: 0.9rem;
        color: #7f8c8d;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .action-buttons {
        display: flex;
        gap: 1rem;
        justify-content: center;
        margin: 2rem 0;
        flex-wrap: wrap;
    }
    
    .action-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem 2rem;
        border: none;
        border-radius: 12px;
        font-size: 1.1rem;
        font-weight: 600;
        text-decoration: none;
        display: inline-block;
        transition: all 0.3s ease;
        box-shadow: 0 6px 20px rgba(102,126,234,0.3);
    }
    
    .action-button:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 30px rgba(102,126,234,0.4);
        color: white;
        text-decoration: none;
    }
    
    .tech-stack {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 2rem 0;
        text-align: center;
    }
    
    .tech-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 1rem;
    }
    
    .tech-badges {
        display: flex;
        justify-content: center;
        gap: 1rem;
        flex-wrap: wrap;
    }
    
    .tech-badge {
        background: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 500;
        color: #2c3e50;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    @media (max-width: 768px) {
        .welcome-title {
            font-size: 2rem;
        }
        .action-buttons {
            flex-direction: column;
            align-items: center;
        }
        .action-button {
            width: 80%;
            text-align: center;
        }
    }
</style>
""", unsafe_allow_html=True)

@require_authentication
def main():
    """Main application with enhanced welcome interface."""
    
    # Welcome header
    st.markdown("""
    <div class="welcome-header">
        <div class="welcome-title">🚨 Disaster Relief Command Center</div>
        <div class="welcome-subtitle">AI-Powered Emergency Response & Resource Optimization Platform</div>
        <div class="action-buttons">
            <a href="?page=dashboard" class="action-button">🚀 Launch Dashboard</a>
            <a href="?page=prediction" class="action-button">🔮 Make Prediction</a>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # System stats
    st.markdown("""
    <div class="stats-container">
        <div class="stat-item">
            <span class="stat-number">96%</span>
            <span class="stat-label">ML Accuracy</span>
        </div>
        <div class="stat-item">
            <span class="stat-number">1000+</span>
            <span class="stat-label">Disasters Analyzed</span>
        </div>
        <div class="stat-item">
            <span class="stat-number">3</span>
            <span class="stat-label">Severity Levels</span>
        </div>
        <div class="stat-item">
            <span class="stat-number">24/7</span>
            <span class="stat-label">Monitoring</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature overview
    st.markdown("## 🌟 Platform Capabilities")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">🤖</span>
            <div class="feature-title">AI Severity Prediction</div>
            <div class="feature-description">
                Advanced Random Forest algorithm analyzes disaster patterns to predict severity levels 
                with 96% accuracy. Supports real-time and batch processing.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">📊</span>
            <div class="feature-title">Interactive Analytics</div>
            <div class="feature-description">
                Comprehensive data visualization with geographic heatmaps, time series analysis, 
                and real-time metrics for informed decision making.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">📦</span>
            <div class="feature-title">Smart Resource Allocation</div>
            <div class="feature-description">
                Priority-based algorithm optimizes resource distribution with 50%/30%/20% allocation 
                strategy for High/Medium/Low severity disasters.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">🔐</span>
            <div class="feature-title">Secure Authentication</div>
            <div class="feature-description">
                Enterprise-grade security with Supabase authentication, role-based access control, 
                and encrypted data transmission.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Technology stack
    st.markdown("""
    <div class="tech-stack">
        <div class="tech-title">🛠️ Powered By Advanced Technology</div>
        <div class="tech-badges">
            <span class="tech-badge">Python 3.13</span>
            <span class="tech-badge">Streamlit</span>
            <span class="tech-badge">Scikit-learn</span>
            <span class="tech-badge">Plotly</span>
            <span class="tech-badge">Supabase</span>
            <span class="tech-badge">Random Forest ML</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation buttons
    st.markdown("## 🚀 Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📈 Dashboard", type="primary", use_container_width=True):
            st.switch_page("dashboard_enhanced.py")
    
    with col2:
        if st.button("🔮 AI Prediction", type="primary", use_container_width=True):
            st.switch_page("dashboard_enhanced.py")
    
    with col3:
        if st.button("📊 Analytics", type="primary", use_container_width=True):
            st.switch_page("dashboard_enhanced.py")
    
    with col4:
        if st.button("⚙️ Bulk Process", type="primary", use_container_width=True):
            st.switch_page("dashboard_enhanced.py")
    
    # Additional information
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 📚 How It Works
        
        1. **Data Input**: Enter disaster details or upload CSV files
        2. **AI Analysis**: Machine learning model analyzes patterns
        3. **Severity Prediction**: Get High/Medium/Low classification
        4. **Resource Allocation**: Receive optimized distribution plan
        5. **Real-time Monitoring**: Track and adjust allocations
        """)
    
    with col2:
        st.markdown("""
        ### 🎯 Key Benefits
        
        - **96% Prediction Accuracy**: Reliable severity classification
        - **Instant Processing**: Real-time disaster analysis
        - **Optimized Allocation**: Evidence-based resource distribution
        - **Interactive Dashboards**: Visual insights and analytics
        - **Scalable Architecture**: Handle thousands of disasters
        """)
    
    # Footer information
    st.markdown("""
    ---
    <div style="text-align: center; color: #7f8c8d; padding: 2rem 0;">
        <p><strong>Disaster Relief Resource Optimizer</strong> - Saving lives through intelligent resource allocation</p>
        <p>Built with ❤️ using AI and modern web technologies</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()