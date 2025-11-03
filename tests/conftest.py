import pytest
from project import create_app, db, socketio
from project.models import User, Board
from config import TestConfig
from project import bcrypt

@pytest.fixture(scope='session')
def app():
    """Create a test app instance."""
    app = create_app(TestConfig)
    return app

@pytest.fixture(scope='function')
def db_session(app):
    """
    Creates a new database session for each test, rolling back changes afterward.
    This ensures test isolation.
    """
    with app.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def client(app):
    """A test client for making HTTP requests."""
    with app.test_client() as client:
        yield client

@pytest.fixture(scope='function')
def socket_client(app):
    """A test client for Socket.IO."""
    return socketio.test_client(app)

@pytest.fixture(scope='function')
def registered_user(db_session):
    """A fixture to create a pre-registered user."""
    hashed_password = bcrypt.generate_password_hash('password123').decode('utf-8')
    user = User(username='testuser', email='test@example.com', password_hash=hashed_password)
    db_session.session.add(user)
    db_session.session.commit()
    return user

@pytest.fixture(scope='function')
def registered_user_2(db_session):
    """A second user for sharing tests."""
    hashed_password = bcrypt.generate_password_hash('password456').decode('utf-8')
    user = User(username='testuser2', email='test2@example.com', password_hash=hashed_password)
    db_session.session.add(user)
    db_session.session.commit()
    return user

@pytest.fixture(scope='function')
def logged_in_client(client, registered_user):
    """A test client that is already logged in."""
    client.post('/auth/login', data={
        'email': registered_user.email,
        'password': 'password123'
    }, follow_redirects=True)
    yield client
    client.get('/auth/logout', follow_redirects=True)