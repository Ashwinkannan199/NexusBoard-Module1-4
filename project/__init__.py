from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_socketio import SocketIO # Import SocketIO
from config import Config

# Initialize extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
socketio = SocketIO() # Initialize SocketIO

# Configure the login manager 
# 'auth.login' is the function name of our login route
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'


def create_app(config_class=Config):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Bind extensions to the app
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    socketio.init_app(app) # Bind SocketIO to the app

    # Register blueprints
    from project.main.routes import main
    from project.auth.routes import auth
    
    app.register_blueprint(main)
    app.register_blueprint(auth, url_prefix='/auth') # Add /auth prefix

    # Import events to register socket handlers
    from project.main import events
    
    return app