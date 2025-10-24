# 🚨 Disaster Relief Resource Optimizer

A comprehensive AI-powered web application for disaster severity prediction and optimal resource allocation using Machine Learning and Supabase authentication.

## 📋 Features

- **🤖 ML Prediction**: Random Forest Classifier for disaster severity prediction (Low/Medium/High)
- **📊 Resource Allocation**: Priority-based algorithm for optimal distribution of relief resources
- **📈 Data Analytics**: Interactive visualizations and insights from historical disaster data
- **👥 User Authentication**: Secure signup/login system with Supabase integration
- **📁 Bulk Processing**: Handle multiple disasters simultaneously
- **🌐 Web Interface**: User-friendly Streamlit application

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Step 1: Clone and Navigate
```bash
cd disaster-relief-optimizer
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Set Up Authentication (Optional)

#### Option A: Use Demo Mode (No Setup Required)
- The app runs in demo mode by default
- Demo accounts: `admin@disaster.com / admin123` and `user@disaster.com / user123`

#### Option B: Connect to Supabase (Full Features)
1. Create a Supabase project at [supabase.com](https://supabase.com)
2. Copy the SQL schema from `src/auth.py` into your Supabase SQL Editor
3. Update credentials in `src/auth.py`:
   ```python
   SUPABASE_URL = "your-project-url"
   SUPABASE_KEY = "your-anon-key"
   ```

## 🚀 Running the Application

### Step 1: Train the ML Model
```bash
python train_model.py
```

### Step 2: Launch the Web App

#### With Authentication:
```bash
streamlit run app_with_auth.py
```

#### Without Authentication (Basic Version):
```bash
streamlit run app.py
```

### Step 3: Access the Application
Open your browser and go to `http://localhost:8501`

## 📂 Project Structure

```
disaster-relief-optimizer/
├── src/
│   ├── data_preprocessing.py    # Data cleaning and feature engineering
│   ├── ml_model.py             # Random Forest model implementation
│   ├── resource_allocator.py   # Resource allocation algorithm
│   ├── data_exploration.py     # Dataset analysis and visualization
│   └── auth.py                 # Supabase authentication system
├── data/
│   ├── disaster_data.csv       # Sample disaster dataset
│   └── dataset_exploration.png # Data visualization output
├── models/
│   ├── model.pkl              # Trained Random Forest model
│   └── preprocessor.pkl       # Data preprocessing pipeline
├── app.py                     # Main Streamlit application
├── app_with_auth.py          # Authentication-enabled app
├── train_model.py            # Model training script
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## 🎯 Usage Guide

### 1. Home Page
- Overview of the application features
- Dataset statistics and recent disasters preview

### 2. Prediction Page
- Input disaster details (type, location, casualties, damages)
- Get ML-powered severity prediction (Low/Medium/High)
- Receive resource allocation recommendations
- View confidence scores and allocation breakdown

### 3. Analytics Page
- Interactive charts showing disaster patterns
- Geographic distribution analysis
- Severity trends over time
- Impact correlation analysis

### 4. Bulk Processing
- Upload CSV file with multiple disasters
- Get batch predictions and resource allocations
- Download results and allocation reports

## 🗄️ Database Schema (Supabase)

### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE,
    role TEXT DEFAULT 'user'
);
```

### Predictions Table
```sql
CREATE TABLE predictions (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    disaster_type TEXT NOT NULL,
    people_affected INTEGER,
    predicted_severity TEXT,
    created_at TIMESTAMP WITH TIME ZONE
);
```

### Resource Allocations Table
```sql
CREATE TABLE resource_allocations (
    id UUID PRIMARY KEY,
    prediction_id UUID REFERENCES predictions(id),
    food_kits_allocated INTEGER,
    water_packs_allocated INTEGER,
    medicine_kits_allocated INTEGER,
    shelter_units_allocated INTEGER,
    fulfillment_rate DECIMAL(5,2)
);
```

## 🤖 Machine Learning Model

### Algorithm: Random Forest Classifier
- **Training Data**: Historical disaster records with features like disaster type, location, casualties, and damages
- **Target Variable**: Severity labels (Low/Medium/High) based on impact thresholds
- **Features**: Year, disaster type, state, district, people affected, deaths, damages
- **Accuracy**: ~96% on test set
- **Train/Test Split**: 80/20

### Severity Classification Rules:
- **High**: Significant casualties, damages, or people affected (top tier impact)
- **Medium**: Moderate impact across multiple factors
- **Low**: Limited impact with lower casualties and damages

## 📊 Resource Allocation Algorithm

### Priority-Based Distribution:
- **High Severity**: 50% of available resources
- **Medium Severity**: 30% of available resources  
- **Low Severity**: 20% of available resources

### Resource Types:
- Food Kits
- Water Packs
- Medicine Kits
- Shelter Units

### Disaster-Specific Adjustments:
- **Floods**: Increased water and shelter allocation
- **Earthquakes**: Enhanced shelter and medical supplies
- **Droughts**: Prioritized water and food distribution
- **Cyclones**: Balanced shelter and water allocation

## 🔧 Configuration

### Environment Variables (Optional)
Create a `.env` file:
```
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key
```

### Model Parameters
Adjust in `src/ml_model.py`:
```python
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42,
    class_weight='balanced'
)
```

### Severity Thresholds
Modify in `src/data_preprocessing.py`:
```python
severity_thresholds = {
    'deaths': {'low': 10, 'medium': 100},
    'affected': {'low': 1000, 'medium': 10000},
    'damages': {'low': 1000000, 'medium': 10000000}
}
```

## 📈 Performance Metrics

### Model Performance:
- **Overall Accuracy**: 96%
- **High Severity**: Precision=1.00, Recall=0.56, F1=0.71
- **Medium Severity**: Precision=0.92, Recall=1.00, F1=0.96
- **Low Severity**: Precision=1.00, Recall=1.00, F1=1.00

### Top Feature Importance:
1. Damages (30.6%)
2. People Affected (30.1%)
3. Deaths (26.5%)
4. Disaster Type (4.1%)
5. Year (3.6%)

## 🐛 Troubleshooting

### Common Issues:

1. **Model not found error**
   ```bash
   python train_model.py
   ```

2. **Supabase connection error**
   - Check credentials in `src/auth.py`
   - Verify Supabase project is active

3. **Package installation issues**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Streamlit port already in use**
   ```bash
   streamlit run app.py --server.port 8502
   ```

## 🚀 Deployment

### Streamlit Cloud
1. Push code to GitHub repository
2. Connect to Streamlit Cloud
3. Add environment variables for Supabase

### Local Production
```bash
streamlit run app_with_auth.py --server.port 8501 --server.address 0.0.0.0
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Kaggle for the disaster dataset
- Supabase for authentication infrastructure
- Streamlit for the web framework
- Scikit-learn for machine learning capabilities

## 📞 Support

For issues and questions:
- Create an issue in the GitHub repository
- Check the troubleshooting section above
- Review the code comments for implementation details

---

**Built with ❤️ for disaster relief optimization**