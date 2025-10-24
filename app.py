"""
Main Streamlit web application for Disaster Relief Resource Optimizer.
Features: ML predictions, resource allocation, and data visualizations.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import joblib
import os
import sys

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from data_preprocessing import DisasterDataPreprocessor
from ml_model import DisasterSeverityModel
from resource_allocator import ResourceAllocator

# Configure page
st.set_page_config(
    page_title="Disaster Relief Resource Optimizer",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .severity-high { color: #ff4b4b; font-weight: bold; }
    .severity-medium { color: #ffa500; font-weight: bold; }
    .severity-low { color: #00c851; font-weight: bold; }
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

def create_disaster_type_chart(df):
    """Create bar chart for disaster types distribution."""
    disaster_counts = df['disaster_type'].value_counts()
    
    fig = px.bar(
        x=disaster_counts.index,
        y=disaster_counts.values,
        title="Distribution of Disaster Types",
        labels={'x': 'Disaster Type', 'y': 'Count'},
        color=disaster_counts.values,
        color_continuous_scale='viridis'
    )
    
    fig.update_layout(
        showlegend=False,
        height=400,
        title_x=0.5
    )
    
    return fig

def create_resource_allocation_pie_chart(allocation_result):
    """Create pie chart for resource allocation."""
    if 'allocated' not in allocation_result:
        return None
    
    allocated = allocation_result['allocated']
    
    # Filter out zero allocations
    non_zero_allocations = {k: v for k, v in allocated.items() if v > 0}
    
    if not non_zero_allocations:
        return None
    
    fig = px.pie(
        values=list(non_zero_allocations.values()),
        names=list(non_zero_allocations.keys()),
        title="Resource Allocation Distribution",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig.update_layout(
        height=400,
        title_x=0.5
    )
    
    return fig

def create_severity_timeline(df):
    """Create timeline showing disasters by severity over years."""
    # Create severity labels for the dataset
    preprocessor = DisasterDataPreprocessor()
    df_with_severity = preprocessor.create_severity_labels(df.copy())
    
    # Group by year and severity
    yearly_severity = df_with_severity.groupby(['year', 'severity']).size().reset_index(name='count')
    
    fig = px.line(
        yearly_severity,
        x='year',
        y='count',
        color='severity',
        title="Disaster Severity Trends Over Time",
        labels={'count': 'Number of Disasters', 'year': 'Year'},
        color_discrete_map={'High': '#ff4b4b', 'Medium': '#ffa500', 'Low': '#00c851'}
    )
    
    fig.update_layout(
        height=400,
        title_x=0.5,
        legend_title="Severity Level"
    )
    
    return fig

def display_prediction_result(severity, confidence_scores=None):
    """Display prediction result with appropriate styling."""
    if severity == 'High':
        st.markdown(f'<p class="severity-high">🔴 Predicted Severity: {severity}</p>', unsafe_allow_html=True)
    elif severity == 'Medium':
        st.markdown(f'<p class="severity-medium">🟡 Predicted Severity: {severity}</p>', unsafe_allow_html=True)
    else:
        st.markdown(f'<p class="severity-low">🟢 Predicted Severity: {severity}</p>', unsafe_allow_html=True)
    
    if confidence_scores is not None:
        st.subheader("Confidence Scores")
        for class_name, score in confidence_scores.items():
            st.write(f"**{class_name}**: {score:.2%}")

def main():
    """Main application function."""
    # Header
    st.markdown('<h1 class="main-header">🚨 Disaster Relief Resource Optimizer</h1>', unsafe_allow_html=True)
    
    # Load model and data
    model, preprocessor, model_error = load_model_and_preprocessor()
    dataset, data_error = load_dataset()
    
    if model_error:
        st.error(model_error)
        st.info("Please run `python train_model.py` to train the model first.")
        return
    
    if data_error:
        st.error(data_error)
        return
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["🏠 Home", "🔮 Prediction", "📊 Analytics", "⚙️ Bulk Processing"]
    )
    
    if page == "🏠 Home":
        show_home_page(dataset)
    elif page == "🔮 Prediction":
        show_prediction_page(model, preprocessor)
    elif page == "📊 Analytics":
        show_analytics_page(dataset)
    elif page == "⚙️ Bulk Processing":
        show_bulk_processing_page(model, preprocessor)

def show_home_page(dataset):
    """Display home page with overview."""
    st.header("Welcome to Disaster Relief Resource Optimizer")
    
    st.markdown("""
    This application uses **Machine Learning** to predict disaster severity and optimize resource allocation 
    for emergency relief operations.
    
    ### Features:
    - 🤖 **ML Prediction**: Random Forest model to predict disaster severity (Low/Medium/High)
    - 📊 **Resource Allocation**: Priority-based algorithm for optimal resource distribution
    - 📈 **Data Analytics**: Visualizations and insights from historical disaster data
    - 📁 **Bulk Processing**: Handle multiple disasters simultaneously
    """)
    
    # Dataset overview
    if dataset is not None:
        st.subheader("Dataset Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Records", len(dataset))
        
        with col2:
            st.metric("Disaster Types", dataset['disaster_type'].nunique())
        
        with col3:
            st.metric("Years Covered", f"{dataset['year'].min()}-{dataset['year'].max()}")
        
        with col4:
            total_affected = dataset['people_affected'].sum()
            st.metric("Total People Affected", f"{total_affected:,.0f}")
        
        # Recent disasters preview
        st.subheader("Recent Disasters (Sample)")
        recent_data = dataset.nlargest(5, 'year')[['year', 'disaster_type', 'state', 'people_affected', 'deaths']]
        st.dataframe(recent_data, use_container_width=True)

def show_prediction_page(model, preprocessor):
    """Display prediction page with input form."""
    st.header("🔮 Disaster Severity Prediction")
    
    st.markdown("Enter disaster details to predict severity and get resource allocation recommendations.")
    
    # Input form
    with st.form("prediction_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            year = st.number_input("Year", min_value=2000, max_value=2030, value=2024)
            disaster_type = st.selectbox(
                "Disaster Type",
                ['flood', 'earthquake', 'cyclone', 'drought', 'landslide', 'wildfire', 'tsunami']
            )
            state = st.selectbox(
                "State/Region",
                ['California', 'Texas', 'Florida', 'New York', 'India', 'Japan', 'Philippines', 'Indonesia']
            )
            district = st.selectbox("District", ['District A', 'District B', 'District C', 'District D', 'District E'])
        
        with col2:
            people_affected = st.number_input("People Affected", min_value=1, value=1000)
            deaths = st.number_input("Deaths", min_value=0, value=10)
            damages = st.number_input("Damages (USD)", min_value=0, value=1000000)
        
        # Available resources section
        st.subheader("Available Resources")
        col3, col4, col5, col6 = st.columns(4)
        
        with col3:
            food_kits = st.number_input("Food Kits", min_value=0, value=5000)
        with col4:
            water_packs = st.number_input("Water Packs", min_value=0, value=8000)
        with col5:
            medicine_kits = st.number_input("Medicine Kits", min_value=0, value=2000)
        with col6:
            shelter_units = st.number_input("Shelter Units", min_value=0, value=1500)
        
        submitted = st.form_submit_button("Predict & Allocate Resources")
    
    if submitted:
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
            # Preprocess input
            processed_input = preprocessor.preprocess_single_input(input_data)
            
            # Make prediction
            prediction = model.predict(processed_input)[0]
            probabilities = model.predict_proba(processed_input)[0]
            
            # Get class names from model
            class_names = model.model.classes_
            confidence_scores = dict(zip(class_names, probabilities))
            
            # Display prediction
            st.subheader("Prediction Results")
            display_prediction_result(prediction, confidence_scores)
            
            # Resource allocation
            st.subheader("Resource Allocation Recommendation")
            
            allocator = ResourceAllocator()
            available_resources = {
                'Food Kits': food_kits,
                'Water Packs': water_packs,
                'Medicine Kits': medicine_kits,
                'Shelter Units': shelter_units
            }
            
            allocation_result = allocator.allocate_single_disaster(
                prediction, people_affected, disaster_type, available_resources
            )
            
            if allocation_result:
                # Display allocation table
                allocation_df = pd.DataFrame([
                    {
                        'Resource Type': resource,
                        'Needed': allocation_result['needed'].get(resource, 0),
                        'Allocated': allocation_result['allocated'].get(resource, 0),
                        'Unmet Need': allocation_result['unmet_needs'].get(resource, 0)
                    }
                    for resource in available_resources.keys()
                ])
                
                st.dataframe(allocation_df, use_container_width=True)
                
                # Fulfillment rate
                fulfillment_rate = allocation_result.get('fulfillment_rate', 0) * 100
                st.metric("Overall Fulfillment Rate", f"{fulfillment_rate:.1f}%")
                
                # Pie chart for allocation
                pie_chart = create_resource_allocation_pie_chart(allocation_result)
                if pie_chart:
                    st.plotly_chart(pie_chart, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error during prediction: {str(e)}")

def show_analytics_page(dataset):
    """Display analytics page with visualizations."""
    st.header("📊 Data Analytics & Insights")
    
    # Disaster types distribution
    st.subheader("Disaster Types Distribution")
    disaster_chart = create_disaster_type_chart(dataset)
    st.plotly_chart(disaster_chart, use_container_width=True)
    
    # Severity trends over time
    st.subheader("Disaster Severity Trends")
    severity_chart = create_severity_timeline(dataset)
    st.plotly_chart(severity_chart, use_container_width=True)
    
    # Geographic distribution
    st.subheader("Geographic Distribution")
    state_counts = dataset['state'].value_counts()
    
    fig_geo = px.bar(
        x=state_counts.values,
        y=state_counts.index,
        orientation='h',
        title="Disasters by State/Region",
        labels={'x': 'Number of Disasters', 'y': 'State/Region'}
    )
    fig_geo.update_layout(height=400, title_x=0.5)
    st.plotly_chart(fig_geo, use_container_width=True)
    
    # Impact analysis
    st.subheader("Impact Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # People affected vs damages
        fig_impact = px.scatter(
            dataset,
            x='people_affected',
            y='damages',
            color='disaster_type',
            title="People Affected vs Economic Damages",
            labels={'people_affected': 'People Affected', 'damages': 'Damages (USD)'},
            log_x=True,
            log_y=True
        )
        fig_impact.update_layout(height=400, title_x=0.5)
        st.plotly_chart(fig_impact, use_container_width=True)
    
    with col2:
        # Deaths vs people affected
        fig_casualties = px.scatter(
            dataset,
            x='people_affected',
            y='deaths',
            color='disaster_type',
            title="Deaths vs People Affected",
            labels={'people_affected': 'People Affected', 'deaths': 'Deaths'},
            log_x=True,
            log_y=True
        )
        fig_casualties.update_layout(height=400, title_x=0.5)
        st.plotly_chart(fig_casualties, use_container_width=True)

def show_bulk_processing_page(model, preprocessor):
    """Display bulk processing page for multiple disasters."""
    st.header("⚙️ Bulk Disaster Processing")
    
    st.markdown("Upload a CSV file with multiple disasters or use the sample template below.")
    
    # Sample template
    if st.button("Download Sample Template"):
        sample_data = pd.DataFrame({
            'year': [2024, 2024, 2024],
            'disaster_type': ['earthquake', 'flood', 'cyclone'],
            'state': ['California', 'Texas', 'Florida'],
            'district': ['District A', 'District B', 'District C'],
            'people_affected': [5000, 3000, 8000],
            'deaths': [50, 20, 100],
            'damages': [10000000, 5000000, 15000000]
        })
        
        csv = sample_data.to_csv(index=False)
        st.download_button(
            label="Download CSV Template",
            data=csv,
            file_name="disaster_template.csv",
            mime="text/csv"
        )
    
    # File upload
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file is not None:
        try:
            # Read uploaded data
            bulk_data = pd.read_csv(uploaded_file)
            st.subheader("Uploaded Data Preview")
            st.dataframe(bulk_data.head(), use_container_width=True)
            
            # Available resources for bulk processing
            st.subheader("Total Available Resources")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_food = st.number_input("Total Food Kits", min_value=0, value=50000)
            with col2:
                total_water = st.number_input("Total Water Packs", min_value=0, value=80000)
            with col3:
                total_medicine = st.number_input("Total Medicine Kits", min_value=0, value=20000)
            with col4:
                total_shelter = st.number_input("Total Shelter Units", min_value=0, value=15000)
            
            if st.button("Process All Disasters"):
                # Process each disaster
                results = []
                allocator = ResourceAllocator()
                
                available_resources = {
                    'Food Kits': total_food,
                    'Water Packs': total_water,
                    'Medicine Kits': total_medicine,
                    'Shelter Units': total_shelter
                }
                
                disasters_for_allocation = []
                
                for idx, row in bulk_data.iterrows():
                    try:
                        # Predict severity
                        input_data = row.to_dict()
                        processed_input = preprocessor.preprocess_single_input(input_data)
                        prediction = model.predict(processed_input)[0]
                        
                        # Prepare for allocation
                        disaster_info = {
                            'severity': prediction,
                            'people_affected': row['people_affected'],
                            'disaster_type': row['disaster_type'],
                            'location': f"{row['state']}, {row['district']}"
                        }
                        disasters_for_allocation.append(disaster_info)
                        
                        results.append({
                            'Index': idx + 1,
                            'Location': f"{row['state']}, {row['district']}",
                            'Disaster Type': row['disaster_type'],
                            'People Affected': row['people_affected'],
                            'Predicted Severity': prediction,
                            'Deaths': row['deaths'],
                            'Damages': row['damages']
                        })
                    except Exception as e:
                        st.error(f"Error processing row {idx + 1}: {str(e)}")
                
                # Display predictions
                if results:
                    st.subheader("Severity Predictions")
                    results_df = pd.DataFrame(results)
                    st.dataframe(results_df, use_container_width=True)
                    
                    # Perform bulk allocation
                    if disasters_for_allocation:
                        st.subheader("Resource Allocation Results")
                        allocation_summary = allocator.allocate_resources(disasters_for_allocation, available_resources)
                        
                        # Display summary statistics
                        summary_stats = allocation_summary['summary_stats']
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total Disasters", summary_stats['total_disasters'])
                        with col2:
                            st.metric("Total People Affected", f"{summary_stats['total_people_affected']:,}")
                        with col3:
                            avg_fulfillment = np.mean(list(summary_stats['avg_fulfillment_by_severity'].values()))
                            st.metric("Average Fulfillment", f"{avg_fulfillment:.1f}%")
                        
                        # Resource utilization
                        st.subheader("Resource Utilization")
                        utilization_data = []
                        for resource, rate in summary_stats['resource_utilization'].items():
                            utilization_data.append({'Resource': resource, 'Utilization (%)': rate})
                        
                        utilization_df = pd.DataFrame(utilization_data)
                        
                        fig_util = px.bar(
                            utilization_df,
                            x='Resource',
                            y='Utilization (%)',
                            title="Resource Utilization Rates",
                            color='Utilization (%)',
                            color_continuous_scale='viridis'
                        )
                        fig_util.update_layout(height=400, title_x=0.5)
                        st.plotly_chart(fig_util, use_container_width=True)
                        
                        # Detailed allocation table
                        st.subheader("Detailed Allocation by Disaster")
                        allocation_details = []
                        for allocation in allocation_summary['allocations']:
                            allocation_details.append({
                                'Location': allocation['location'],
                                'Severity': allocation['severity'],
                                'People Affected': allocation['people_affected'],
                                'Food Allocated': allocation['allocated']['Food Kits'],
                                'Water Allocated': allocation['allocated']['Water Packs'],
                                'Medicine Allocated': allocation['allocated']['Medicine Kits'],
                                'Shelter Allocated': allocation['allocated']['Shelter Units'],
                                'Fulfillment Rate (%)': f"{allocation['fulfillment_rate']*100:.1f}"
                            })
                        
                        allocation_df = pd.DataFrame(allocation_details)
                        st.dataframe(allocation_df, use_container_width=True)
        
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")

if __name__ == "__main__":
    main()