import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration settings
VALID_ACCESS_CODE = os.environ.get('VALID_ACCESS_CODE', 'default-test-code')

# Database configuration
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///schedly.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Email configuration
SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
EMAIL_ADDRESS = os.environ.get('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')

# Validate required environment variables
if not EMAIL_ADDRESS:
    raise ValueError("EMAIL_ADDRESS environment variable is required")
if not EMAIL_PASSWORD:
    raise ValueError("EMAIL_PASSWORD environment variable is required")