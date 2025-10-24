"""
Data preprocessing module for disaster relief resource optimizer.
Handles data cleaning, feature engineering, and preparation for ML model.
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
import warnings
warnings.filterwarnings('ignore')

class DisasterDataPreprocessor:
    def __init__(self):
        self.label_encoders = {}
        self.scaler = StandardScaler()
        self.severity_thresholds = {
            'deaths': {'low': 10, 'medium': 100},
            'affected': {'low': 1000, 'medium': 10000},
            'damages': {'low': 1000000, 'medium': 10000000}  # in currency units
        }
    
    def load_data(self, file_path):
        """Load disaster dataset from CSV file."""
        try:
            df = pd.read_csv(file_path)
            print(f"Dataset loaded successfully. Shape: {df.shape}")
            return df
        except Exception as e:
            print(f"Error loading data: {e}")
            return None
    
    def clean_data(self, df):
        """Handle missing values and data inconsistencies."""
        print("Cleaning data...")
        
        # Make a copy to avoid modifying original
        df_clean = df.copy()
        
        # Convert column names to lowercase and replace spaces with underscores
        df_clean.columns = df_clean.columns.str.lower().str.replace(' ', '_')
        
        # Handle missing values for numerical columns
        numerical_cols = ['deaths', 'people_affected', 'damages']
        for col in numerical_cols:
            if col in df_clean.columns:
                # Fill missing values with median
                df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
                df_clean[col].fillna(df_clean[col].median(), inplace=True)
        
        # Handle missing values for categorical columns
        categorical_cols = ['disaster_type', 'state', 'district']
        for col in categorical_cols:
            if col in df_clean.columns:
                df_clean[col].fillna('Unknown', inplace=True)
        
        # Remove rows with critical missing information
        critical_cols = ['year', 'disaster_type']
        for col in critical_cols:
            if col in df_clean.columns:
                df_clean = df_clean.dropna(subset=[col])
        
        print(f"Data cleaned. Final shape: {df_clean.shape}")
        return df_clean
    
    def create_severity_labels(self, df):
        """Create disaster severity labels based on deaths, affected people, and damages."""
        print("Creating severity labels...")
        
        severity_scores = []
        
        for _, row in df.iterrows():
            score = 0
            
            # Score based on deaths
            deaths = row.get('deaths', 0)
            if deaths >= self.severity_thresholds['deaths']['medium']:
                score += 3
            elif deaths >= self.severity_thresholds['deaths']['low']:
                score += 2
            else:
                score += 1
            
            # Score based on people affected
            affected = row.get('people_affected', 0)
            if affected >= self.severity_thresholds['affected']['medium']:
                score += 3
            elif affected >= self.severity_thresholds['affected']['low']:
                score += 2
            else:
                score += 1
            
            # Score based on damages
            damages = row.get('damages', 0)
            if damages >= self.severity_thresholds['damages']['medium']:
                score += 3
            elif damages >= self.severity_thresholds['damages']['low']:
                score += 2
            else:
                score += 1
            
            severity_scores.append(score)
        
        # Convert scores to labels
        severity_labels = []
        for score in severity_scores:
            if score >= 7:
                severity_labels.append('High')
            elif score >= 5:
                severity_labels.append('Medium')
            else:
                severity_labels.append('Low')
        
        df['severity'] = severity_labels
        print(f"Severity distribution:\n{pd.Series(severity_labels).value_counts()}")
        return df
    
    def encode_categorical_features(self, df, fit=True):
        """Encode categorical variables using label encoding."""
        print("Encoding categorical features...")
        
        df_encoded = df.copy()
        categorical_cols = ['disaster_type', 'state', 'district']
        
        for col in categorical_cols:
            if col in df_encoded.columns:
                if fit:
                    # Fit new encoder
                    self.label_encoders[col] = LabelEncoder()
                    df_encoded[col] = self.label_encoders[col].fit_transform(df_encoded[col].astype(str))
                else:
                    # Use existing encoder
                    if col in self.label_encoders:
                        # Handle unseen categories
                        unique_values = set(df_encoded[col].astype(str))
                        known_values = set(self.label_encoders[col].classes_)
                        unseen_values = unique_values - known_values
                        
                        if unseen_values:
                            # Map unseen values to a default category
                            df_encoded[col] = df_encoded[col].astype(str).apply(
                                lambda x: x if x in known_values else 'Unknown'
                            )
                        
                        df_encoded[col] = self.label_encoders[col].transform(df_encoded[col].astype(str))
        
        return df_encoded
    
    def normalize_features(self, df, fit=True):
        """Normalize numerical features using StandardScaler."""
        print("Normalizing numerical features...")
        
        df_normalized = df.copy()
        numerical_cols = ['year', 'deaths', 'people_affected', 'damages']
        
        # Select only available numerical columns
        available_cols = [col for col in numerical_cols if col in df_normalized.columns]
        
        if available_cols:
            if fit:
                df_normalized[available_cols] = self.scaler.fit_transform(df_normalized[available_cols])
            else:
                df_normalized[available_cols] = self.scaler.transform(df_normalized[available_cols])
        
        return df_normalized
    
    def prepare_features_and_target(self, df):
        """Prepare feature matrix X and target vector y."""
        print("Preparing features and target...")
        
        # Define feature columns (exclude target and non-feature columns)
        feature_cols = ['year', 'disaster_type', 'state', 'district', 'people_affected', 'deaths', 'damages']
        available_features = [col for col in feature_cols if col in df.columns]
        
        X = df[available_features]
        y = df['severity']
        
        print(f"Features shape: {X.shape}")
        print(f"Target shape: {y.shape}")
        print(f"Features: {available_features}")
        
        return X, y
    
    def preprocess_data(self, file_path, test_size=0.2, random_state=42):
        """Complete preprocessing pipeline."""
        print("Starting data preprocessing pipeline...")
        
        # Load data
        df = self.load_data(file_path)
        if df is None:
            return None, None, None, None
        
        # Clean data
        df_clean = self.clean_data(df)
        
        # Create severity labels
        df_with_severity = self.create_severity_labels(df_clean)
        
        # Encode categorical features
        df_encoded = self.encode_categorical_features(df_with_severity, fit=True)
        
        # Normalize features
        df_normalized = self.normalize_features(df_encoded, fit=True)
        
        # Prepare features and target
        X, y = self.prepare_features_and_target(df_normalized)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )
        
        print("Data preprocessing completed successfully!")
        print(f"Training set: {X_train.shape}")
        print(f"Test set: {X_test.shape}")
        
        return X_train, X_test, y_train, y_test
    
    def preprocess_single_input(self, input_data):
        """Preprocess a single input for prediction."""
        # Convert input to DataFrame
        df_input = pd.DataFrame([input_data])
        
        # Apply same preprocessing steps (without fitting)
        df_encoded = self.encode_categorical_features(df_input, fit=False)
        df_normalized = self.normalize_features(df_encoded, fit=False)
        
        # Select feature columns in the same order as training
        feature_cols = ['year', 'disaster_type', 'state', 'district', 'people_affected', 'deaths', 'damages']
        available_features = [col for col in feature_cols if col in df_normalized.columns]
        
        return df_normalized[available_features]

if __name__ == "__main__":
    # Test the preprocessing pipeline
    preprocessor = DisasterDataPreprocessor()
    # Uncomment the following lines when you have the dataset
    # X_train, X_test, y_train, y_test = preprocessor.preprocess_data('data/disaster_data.csv')