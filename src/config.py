import os
from pathlib import Path

# Project root directory
ROOT_DIR = Path(__file__).parent.parent

# Data directories
RAW_DATA_DIR = ROOT_DIR / "data" / "raw"
PROCESSED_DATA_DIR = ROOT_DIR / "data" / "processed"

# API endpoints
API_ENDPOINTS = {
    'gcp': 'https://api.cloud.google.com/sustainability',  # Example endpoint
    'aws': 'https://api.aws.amazon.com/sustainability',    # Example endpoint
    'azure': 'https://api.azure.com/sustainability'        # Example endpoint
}

# Model parameters
MODEL_PARAMS = {
    'lstm': {
        'units': 128,
        'layers': 2,
        'dropout': 0.2
    },
    'xgboost': {
        'max_depth': 6,
        'learning_rate': 0.1,
        'n_estimators': 100
    }
} 