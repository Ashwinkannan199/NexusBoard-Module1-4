import pytest
from project.models import Board, List, Card, User

# --- Board CRUD ---

def test_create_board(logged_in_client, db_session, registered_user):
    """Test creating a new board."""
    response = logged_in_client.post('/dashboard', data={
        'name': 'My Test Board'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"New board created!" in response.data
    assert b"My Test Board" in response.data
    
    board = Board.query.filter_by(name='My Test Board').first()
    assert board is not None
    assert board.owner == registered_user

def test_edit_board(logged_in_client, db_session, registered_user):
    """Test editing a board (only owner)."""
    board = Board(name="Old Name", owner=registered_user)
    db_session.session.add(board)
    db_session.session.commit()
    
    response = logged_in_client.post(f'/board/edit/{board.id}', data={
        'name': 'New Name'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"Board has been updated!" in response.data
    assert b"New Name" in response.data
    
    updated_board = Board.query.get(board.id)
    assert updated_board.name == 'New Name'

def test_delete_board(logged_in_client, db_session, registered_user):
    """Test deleting a board (only owner)."""
    board = Board(name="To Be Deleted", owner=registered_user)
    db_session.session.add(board)
    db_session.session.commit()
    
    response = logged_in_client.post(f'/board/delete/{board.id}', follow_redirects=True)
    
    assert response.status_code == 200
    assert b"Board deleted." in response.data
    assert Board.query.get(board.id) is None

# --- List & Card CRUD (Simplified examples) ---

@pytest.fixture
def test_board(db_session, registered_user):
    """Fixture to create a board for list/card tests."""
    board = Board(name="Board for Lists", owner=registered_user)
    db_session.session.add(board)
    db_session.session.commit()
    return board

def test_create_list(logged_in_client, db_session, test_board):
    """Test creating a new list on a board."""
    response = logged_in_client.post(f'/list/create/{test_board.id}', data={
        'name': 'To Do'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"List created!" in response.data
    assert b"To Do" in response.data
    
    list_item = List.query.filter_by(name='To Do').first()
    assert list_item is not None
    assert list_item.board_id == test_board.id

# --- Sharing Tests ---

def test_invite_user(logged_in_client, db_session, test_board, registered_user_2):
    """Test inviting a user to a board."""
    response = logged_in_client.post(f'/board/{test_board.id}/manage', data={
        'email': registered_user_2.email
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"Invited testuser2 to the board." in response.data
    
    board = Board.query.get(test_board.id)
    assert registered_user_2 in board.members

def test_shared_board_access(client, db_session, test_board, registered_user_2):
    """Test that a shared user can access the board."""
    # Add user 2 to the board
    test_board.members.append(registered_user_2)
    db_session.session.commit()
    
    # Log in as user 2
    client.post('/auth/login', data={
        'email': registered_user_2.email,
        'password': 'password456'
    }, follow_redirects=True)
    
    # Try to access the board
    response = client.get(f'/board/{test_board.id}')
    assert response.status_code == 200
    assert b"Board: Board for Lists" in response.data

def test_unauthorized_board_access(client, db_session, test_board, registered_user_2):
    """Test that a non-member cannot access the board."""
    # Log in as user 2 (who is NOT a member)
    client.post('/auth/login', data={
        'email': registered_user_2.email,
        'password': 'password456'
    }, follow_redirects=True)
    
    # Try to access the board
    response = client.get(f'/board/{test_board.id}')
    assert response.status_code == 403 # Forbidden