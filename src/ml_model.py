"""
Machine Learning model module for disaster severity prediction.
Implements Random Forest Classifier with model training and evaluation.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib
import os

class DisasterSeverityModel:
    def __init__(self, n_estimators=100, random_state=42):
        """Initialize Random Forest Classifier."""
        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            random_state=random_state,
            class_weight='balanced'  # Handle class imbalance
        )
        self.is_trained = False
        self.feature_names = None
        self.feature_importance = None
    
    def train(self, X_train, y_train):
        """Train the Random Forest model."""
        print("Training Random Forest model...")
        
        # Store feature names
        if hasattr(X_train, 'columns'):
            self.feature_names = list(X_train.columns)
        else:
            self.feature_names = [f'feature_{i}' for i in range(X_train.shape[1])]
        
        # Train the model
        self.model.fit(X_train, y_train)
        self.is_trained = True
        
        # Calculate feature importance
        self.feature_importance = dict(zip(self.feature_names, self.model.feature_importances_))
        
        print("Model training completed!")
        return self
    
    def evaluate(self, X_test, y_test):
        """Evaluate the trained model."""
        if not self.is_trained:
            print("Model is not trained yet!")
            return None
        
        print("Evaluating model...")
        
        # Make predictions
        y_pred = self.model.predict(X_test)
        
        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"Accuracy: {accuracy:.4f}")
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred))
        print("\nConfusion Matrix:")
        print(confusion_matrix(y_test, y_pred))
        
        # Feature importance
        print("\nTop 5 Most Important Features:")
        sorted_features = sorted(self.feature_importance.items(), key=lambda x: x[1], reverse=True)
        for feature, importance in sorted_features[:5]:
            print(f"{feature}: {importance:.4f}")
        
        return {
            'accuracy': accuracy,
            'predictions': y_pred,
            'classification_report': classification_report(y_test, y_pred, output_dict=True)
        }
    
    def predict(self, X):
        """Make predictions on new data."""
        if not self.is_trained:
            print("Model is not trained yet!")
            return None
        
        return self.model.predict(X)
    
    def predict_proba(self, X):
        """Get prediction probabilities."""
        if not self.is_trained:
            print("Model is not trained yet!")
            return None
        
        return self.model.predict_proba(X)
    
    def save_model(self, filepath):
        """Save the trained model to disk."""
        if not self.is_trained:
            print("Model is not trained yet!")
            return False
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Save model and metadata
            model_data = {
                'model': self.model,
                'feature_names': self.feature_names,
                'feature_importance': self.feature_importance,
                'is_trained': self.is_trained
            }
            
            joblib.dump(model_data, filepath)
            print(f"Model saved successfully to: {filepath}")
            return True
        except Exception as e:
            print(f"Error saving model: {e}")
            return False
    
    def load_model(self, filepath):
        """Load a trained model from disk."""
        try:
            model_data = joblib.load(filepath)
            
            self.model = model_data['model']
            self.feature_names = model_data['feature_names']
            self.feature_importance = model_data['feature_importance']
            self.is_trained = model_data['is_trained']
            
            print(f"Model loaded successfully from: {filepath}")
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            return False
    
    def get_feature_importance(self):
        """Get feature importance as a sorted dictionary."""
        if not self.is_trained:
            return None
        
        return sorted(self.feature_importance.items(), key=lambda x: x[1], reverse=True)

def train_disaster_model(X_train, X_test, y_train, y_test, save_path='models/model.pkl'):
    """Complete model training pipeline."""
    print("Starting model training pipeline...")
    
    # Initialize and train model
    model = DisasterSeverityModel()
    model.train(X_train, y_train)
    
    # Evaluate model
    evaluation_results = model.evaluate(X_test, y_test)
    
    # Save model
    model.save_model(save_path)
    
    print("Model training pipeline completed!")
    return model, evaluation_results

if __name__ == "__main__":
    # Test the model training pipeline
    # This would typically be called after data preprocessing
    print("Disaster Severity Model module loaded successfully!")