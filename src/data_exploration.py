"""
Dataset download and exploration script.
Instructions for downloading the Kaggle disaster dataset.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

def download_kaggle_dataset():
    """
    Instructions for downloading the disaster dataset from Kaggle.
    
    To download the dataset, follow these steps:
    
    1. Install Kaggle API:
       pip install kaggle
    
    2. Set up Kaggle API credentials:
       - Go to https://www.kaggle.com/account
       - Click "Create New API Token"
       - Download kaggle.json file
       - Place it in: ~/.kaggle/kaggle.json (Linux/Mac) or C:/Users/{username}/.kaggle/kaggle.json (Windows)
    
    3. Run the following command in terminal:
       kaggle datasets download -d jseebs/disaster-dataset
    
    4. Extract the downloaded zip file to the data/ directory
    """
    
    print("To download the Kaggle disaster dataset:")
    print("1. Install kaggle: pip install kaggle")
    print("2. Set up API credentials (see function docstring for details)")
    print("3. Run: kaggle datasets download -d jseebs/disaster-dataset")
    print("4. Extract to data/ directory")
    
    # Alternative: Download using Python (requires authentication)
    try:
        import kaggle
        kaggle.api.authenticate()
        kaggle.api.dataset_download_files('jseebs/disaster-dataset', path='data/', unzip=True)
        print("Dataset downloaded successfully!")
    except Exception as e:
        print(f"Kaggle API download failed: {e}")
        print("Please download manually following the instructions above.")

def create_sample_dataset():
    """Create a sample disaster dataset for testing purposes."""
    
    print("Creating sample disaster dataset...")
    
    # Set random seed for reproducibility
    np.random.seed(42)
    
    # Define possible values
    disaster_types = ['flood', 'earthquake', 'cyclone', 'drought', 'landslide', 'wildfire', 'tsunami']
    states = ['California', 'Texas', 'Florida', 'New York', 'India', 'Japan', 'Philippines', 'Indonesia']
    districts = ['District A', 'District B', 'District C', 'District D', 'District E']
    
    # Generate sample data
    n_samples = 1000
    
    data = []
    for i in range(n_samples):
        # Random year between 2000 and 2023
        year = np.random.randint(2000, 2024)
        
        # Random disaster type
        disaster_type = np.random.choice(disaster_types)
        
        # Random location
        state = np.random.choice(states)
        district = np.random.choice(districts)
        
        # Generate realistic numbers based on disaster type
        if disaster_type in ['earthquake', 'tsunami']:
            people_affected = np.random.lognormal(8, 1.5)  # Higher impact
            deaths = np.random.lognormal(3, 1.5)
            damages = np.random.lognormal(15, 1.5)
        elif disaster_type in ['flood', 'cyclone']:
            people_affected = np.random.lognormal(7, 1.2)
            deaths = np.random.lognormal(2.5, 1.2)
            damages = np.random.lognormal(14, 1.2)
        else:  # drought, landslide, wildfire
            people_affected = np.random.lognormal(6.5, 1.0)
            deaths = np.random.lognormal(2, 1.0)
            damages = np.random.lognormal(13, 1.0)
        
        # Add some missing values randomly (10% chance)
        if np.random.random() < 0.1:
            deaths = np.nan
        if np.random.random() < 0.05:
            damages = np.nan
        if np.random.random() < 0.03:
            people_affected = np.nan
        
        data.append({
            'year': year,
            'disaster_type': disaster_type,
            'state': state,
            'district': district,
            'people_affected': int(people_affected) if not pd.isna(people_affected) else np.nan,
            'deaths': int(deaths) if not pd.isna(deaths) else np.nan,
            'damages': int(damages) if not pd.isna(damages) else np.nan
        })
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Save to CSV
    output_path = 'data/disaster_data.csv'
    os.makedirs('data', exist_ok=True)
    df.to_csv(output_path, index=False)
    
    print(f"Sample dataset created: {output_path}")
    print(f"Dataset shape: {df.shape}")
    
    return df

def explore_dataset(file_path):
    """Explore the disaster dataset and generate insights."""
    
    print(f"Loading dataset from: {file_path}")
    
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print("Dataset not found. Creating sample dataset...")
        df = create_sample_dataset()
    
    print("\n" + "="*50)
    print("DATASET EXPLORATION")
    print("="*50)
    
    # Basic information
    print(f"\nDataset Shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    
    # Data types and missing values
    print("\nData Types and Missing Values:")
    print(df.info())
    
    # Statistical summary
    print("\nStatistical Summary:")
    print(df.describe())
    
    # Missing values analysis
    print("\nMissing Values Count:")
    missing_values = df.isnull().sum()
    print(missing_values[missing_values > 0])
    
    # Categorical variables analysis
    print("\nDisaster Types Distribution:")
    if 'disaster_type' in df.columns:
        print(df['disaster_type'].value_counts())
    
    print("\nStates Distribution (top 10):")
    if 'state' in df.columns:
        print(df['state'].value_counts().head(10))
    
    # Numerical variables analysis
    numerical_cols = ['year', 'people_affected', 'deaths', 'damages']
    available_numerical = [col for col in numerical_cols if col in df.columns]
    
    if available_numerical:
        print(f"\nNumerical Variables Summary:")
        print(df[available_numerical].describe())
    
    # Year analysis
    if 'year' in df.columns:
        print(f"\nYear Range: {df['year'].min()} - {df['year'].max()}")
        print("Disasters by Year (top 10):")
        print(df['year'].value_counts().head(10))
    
    return df

def visualize_dataset(df):
    """Create basic visualizations for the dataset."""
    
    print("\nCreating visualizations...")
    
    # Set up the plotting style
    plt.style.use('default')
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Disaster Dataset Exploration', fontsize=16)
    
    # 1. Disaster types distribution
    if 'disaster_type' in df.columns:
        disaster_counts = df['disaster_type'].value_counts()
        axes[0, 0].bar(disaster_counts.index, disaster_counts.values)
        axes[0, 0].set_title('Disaster Types Distribution')
        axes[0, 0].set_xlabel('Disaster Type')
        axes[0, 0].set_ylabel('Count')
        axes[0, 0].tick_params(axis='x', rotation=45)
    
    # 2. Disasters over time
    if 'year' in df.columns:
        year_counts = df['year'].value_counts().sort_index()
        axes[0, 1].plot(year_counts.index, year_counts.values, marker='o')
        axes[0, 1].set_title('Disasters Over Time')
        axes[0, 1].set_xlabel('Year')
        axes[0, 1].set_ylabel('Number of Disasters')
    
    # 3. People affected distribution
    if 'people_affected' in df.columns:
        people_affected_clean = df['people_affected'].dropna()
        if len(people_affected_clean) > 0:
            axes[1, 0].hist(np.log10(people_affected_clean + 1), bins=30, alpha=0.7)
            axes[1, 0].set_title('People Affected Distribution (log scale)')
            axes[1, 0].set_xlabel('Log10(People Affected + 1)')
            axes[1, 0].set_ylabel('Frequency')
    
    # 4. Deaths vs People Affected
    if 'deaths' in df.columns and 'people_affected' in df.columns:
        clean_data = df[['deaths', 'people_affected']].dropna()
        if len(clean_data) > 0:
            axes[1, 1].scatter(clean_data['people_affected'], clean_data['deaths'], alpha=0.6)
            axes[1, 1].set_title('Deaths vs People Affected')
            axes[1, 1].set_xlabel('People Affected')
            axes[1, 1].set_ylabel('Deaths')
            axes[1, 1].set_xscale('log')
            axes[1, 1].set_yscale('log')
    
    plt.tight_layout()
    
    # Save the plot
    os.makedirs('data', exist_ok=True)
    plt.savefig('data/dataset_exploration.png', dpi=300, bbox_inches='tight')
    print("Visualizations saved to: data/dataset_exploration.png")
    
    plt.show()

if __name__ == "__main__":
    # Check if dataset exists, if not create sample data
    dataset_path = 'data/disaster_data.csv'
    
    if not os.path.exists(dataset_path):
        print("Dataset not found. Options:")
        print("1. Download from Kaggle (requires API setup)")
        print("2. Create sample dataset for testing")
        
        choice = input("Enter choice (1 or 2): ").strip()
        
        if choice == '1':
            download_kaggle_dataset()
        else:
            create_sample_dataset()
    
    # Explore the dataset
    df = explore_dataset(dataset_path)
    
    # Create visualizations
    # visualize_dataset(df)  # Uncomment to create plots