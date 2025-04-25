import os
from datetime import timedelta

class Config:
    SECRET_KEY = "super-secret-key"
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'super-secret-key'  # Change this in production!
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=999,minutes=15)  # Token expires in 15 minutes
    JWT_BLACKLIST_ENABLED = True  # Enable token blacklisting
    JWT_BLACKLIST_TOKEN_CHECKS = ['access']  # Blacklist access tokens

    # MLflow Configuration for Model Retraining
    MLFLOW_TRACKING_URI = os.environ.get('MLFLOW_TRACKING_URI', 'http://localhost:5001')
    MODEL_NAME = os.environ.get('MODEL_NAME', 'complaint_response_model')
    
    # Airflow Configuration 
    AIRFLOW_HOME = os.environ.get('AIRFLOW_HOME', os.path.expanduser('~/airflow'))
    AIRFLOW_MAX_RETRIES = int(os.environ.get('AIRFLOW_MAX_RETRIES', 3))
    AIRFLOW_RETRY_DELAY = int(os.environ.get('AIRFLOW_RETRY_DELAY', 30))  # in minutes

    # local model path before retraining
    LOCAL_MODEL_PATH = os.environ.get('LOCAL_MODEL_PATH', 'services/recommendation_model')  

    # Model Parameters
    MAX_INPUT_LENGTH = 128
    MAX_OUTPUT_LENGTH = 512
    MODEL_REFRESH_INTERVAL = 24*60*60  # seconds (1 day)

    # Model Training Configuration
    TRAINING_DATA_THRESHOLD = int(os.environ.get('TRAINING_DATA_THRESHOLD', 50))
    TRAINING_TEST_SPLIT = float(os.environ.get('TRAINING_TEST_SPLIT', 0.1))
    TRAINING_BATCH_SIZE = int(os.environ.get('TRAINING_BATCH_SIZE', 4))
    TRAINING_LEARNING_RATE = float(os.environ.get('TRAINING_LEARNING_RATE', 2e-5))
    TRAINING_EPOCHS = int(os.environ.get('TRAINING_EPOCHS', 3))
