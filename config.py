import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Set Flask configuration variables from .env file."""
    
    # General Config
    SECRET_KEY = os.environ.get('SECRET_KEY')

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Disable CSRF for Postman testing
    WTF_CSRF_ENABLED = False


# --- ADD THIS CLASS ---
class TestConfig(Config):
    """Configuration for testing."""
    TESTING = True
    
    # We set WTForms CSRF protection to False for testing forms
    WTF_CSRF_ENABLED = False 
    
    # Use a separate database for testing.
    # A file-based SQLite database is the simplest option.
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'test.db')
    
    # --- OR ---
    # If you prefer, you can set up a separate PostgreSQL test database
    # and put its URL here (e.g., 'postgresql://user:pass@localhost/nexusboard_test_db')