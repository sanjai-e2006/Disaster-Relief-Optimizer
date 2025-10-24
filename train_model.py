"""
Complete training pipeline for disaster severity prediction model.
Combines data preprocessing and Random Forest model training.
"""

import sys
import os

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from data_preprocessing import DisasterDataPreprocessor
from ml_model import DisasterSeverityModel, train_disaster_model
import pandas as pd
import numpy as np

def main():
    """Main training pipeline."""
    print("Starting Disaster Relief Resource Optimizer Training Pipeline")
    print("=" * 60)
    
    # File paths
    data_file = 'data/disaster_data.csv'
    model_file = 'models/model.pkl'
    
    # Check if data file exists
    if not os.path.exists(data_file):
        print(f"Error: Data file not found at {data_file}")
        print("Please run the data exploration script first to create sample data.")
        return
    
    # Step 1: Data Preprocessing
    print("\n1. DATA PREPROCESSING")
    print("-" * 30)
    
    preprocessor = DisasterDataPreprocessor()
    X_train, X_test, y_train, y_test = preprocessor.preprocess_data(data_file)
    
    if X_train is None:
        print("Error: Data preprocessing failed!")
        return
    
    # Step 2: Model Training
    print("\n2. MODEL TRAINING")
    print("-" * 30)
    
    model, evaluation_results = train_disaster_model(
        X_train, X_test, y_train, y_test, model_file
    )
    
    # Step 3: Results Summary
    print("\n3. TRAINING RESULTS SUMMARY")
    print("-" * 30)
    
    if evaluation_results:
        print(f"Model Accuracy: {evaluation_results['accuracy']:.4f}")
        
        # Print class-wise performance
        class_report = evaluation_results['classification_report']
        print("\nClass-wise Performance:")
        for class_name in ['High', 'Medium', 'Low']:
            if class_name in class_report:
                metrics = class_report[class_name]
                print(f"{class_name:6}: Precision={metrics['precision']:.3f}, "
                      f"Recall={metrics['recall']:.3f}, F1={metrics['f1-score']:.3f}")
        
        # Feature importance
        print("\nTop Feature Importances:")
        feature_importance = model.get_feature_importance()
        if feature_importance:
            for feature, importance in feature_importance[:5]:
                print(f"{feature:15}: {importance:.4f}")
    
    # Step 4: Save preprocessor for later use
    print("\n4. SAVING COMPONENTS")
    print("-" * 30)
    
    import joblib
    preprocessor_file = 'models/preprocessor.pkl'
    os.makedirs('models', exist_ok=True)
    
    try:
        joblib.dump(preprocessor, preprocessor_file)
        print(f"Preprocessor saved to: {preprocessor_file}")
        print(f"Model saved to: {model_file}")
    except Exception as e:
        print(f"Error saving preprocessor: {e}")
    
    print("\nTraining pipeline completed successfully!")
    print("You can now use the trained model in the web application.")

if __name__ == "__main__":
    main()