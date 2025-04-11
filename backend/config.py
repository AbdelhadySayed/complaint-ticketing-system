import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'super-secret-key'  # Change this in production!
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=999,minutes=15)  # Token expires in 15 minutes
    JWT_BLACKLIST_ENABLED = True  # Enable token blacklisting
    JWT_BLACKLIST_TOKEN_CHECKS = ['access']  # Blacklist access tokens