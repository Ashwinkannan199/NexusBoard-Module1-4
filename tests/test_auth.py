import pytest
from project.models import User

def test_index_page(client):
    """Test that the index page loads."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Welcome to NexusBoard" in response.data

def test_user_registration(client, db_session):
    """Test new user registration."""
    response = client.post('/auth/register', data={
        'username': 'newuser',
        'email': 'new@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"Login" in response.data # Should redirect to login
    
    user = User.query.filter_by(email='new@example.com').first()
    assert user is not None
    assert user.username == 'newuser'

def test_user_login(client, registered_user):
    """Test existing user login."""
    response = client.post('/auth/login', data={
        'email': registered_user.email,
        'password': 'password123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"Welcome to your Dashboard" in response.data
    assert b"testuser" in response.data

def test_user_login_wrong_password(client, registered_user):
    """Test login with a wrong password."""
    response = client.post('/auth/login', data={
        'email': registered_user.email,
        'password': 'wrongpassword'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"Login Unsuccessful. Please check email and password." in response.data
    assert b"Welcome to your Dashboard" not in response.data

def test_dashboard_access_logged_out(client):
    """Test that the dashboard is protected."""
    response = client.get('/dashboard', follow_redirects=True)
    assert response.status_code == 200
    assert b"Please log in to access this page" in response.data

def test_dashboard_access_logged_in(logged_in_client):
    """Test that the dashboard is accessible when logged in."""
    response = logged_in_client.get('/dashboard')
    assert response.status_code == 200
    assert b"Welcome to your Dashboard" in response.data

def test_logout(logged_in_client):
    """Test user logout."""
    response = logged_in_client.get('/auth/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b"Welcome to NexusBoard" in response.data
    
    # Verify user is logged out
    response = logged_in_client.get('/dashboard', follow_redirects=True)
    assert b"Please log in to access this page" in response.data