import os
from dotenv import load_dotenv

# Load environment variables from .env file (for local development)
load_dotenv()

# Configuration settings
VALID_ACCESS_CODE = os.environ.get('VALID_ACCESS_CODE', 'default-test-code')

# Database configuration
# Render provides DATABASE_URL for PostgreSQL
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    # Fix for SQLAlchemy 1.4+ which requires postgresql:// instead of postgres://
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

SQLALCHEMY_DATABASE_URI = DATABASE_URL or 'sqlite:///schedly.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Email configuration
SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
EMAIL_ADDRESS = os.environ.get('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')

# Validate required environment variables in production
if os.environ.get('RENDER'):  # Render sets this environment variable
    if not EMAIL_ADDRESS:
        raise ValueError("EMAIL_ADDRESS environment variable is required")
    if not EMAIL_PASSWORD:
        raise ValueError("EMAIL_PASSWORD environment variable is required")