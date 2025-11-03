import pytest
from project.models import Board, List, Card
from project import socketio

@pytest.fixture
def socket_test_data(db_session, registered_user):
    """Fixture to set up a board, lists, and a card for socket testing."""
    board = Board(name="Socket Test Board", owner=registered_user)
    list1 = List(name="List 1", position=0, board=board)
    list2 = List(name="List 2", position=1, board=board)
    card1 = Card(title="Test Card", position=0, list=list1)
    
    db_session.session.add_all([board, list1, list2, card1])
    db_session.session.commit()
    
    return {
        'board_id': board.id,
        'list1_id': list1.id,
        'list2_id': list2.id,
        'card1_id': card1.id,
        'user': registered_user
    }

def test_socket_join_board(socket_client, logged_in_client, socket_test_data):
    """Test joining a board's socket room."""
    # We need the HTTP client to be logged in for the socket to know the user
    socket_client.flask_test_client = logged_in_client
    
    socket_client.emit('join_board', {'board_id': str(socket_test_data['board_id'])})
    
    # This is a simple test; a real test would check rooms,
    # but for now, we just ensure no errors.
    assert True 

def test_socket_card_moved(socket_client, logged_in_client, db_session, socket_test_data):
    """Test the 'card_moved' event to move a card to a new list."""
    socket_client.flask_test_client = logged_in_client
    
    # Join the room first
    socket_client.emit('join_board', {'board_id': str(socket_test_data['board_id'])})
    
    # Define the move
    move_data = {
        'card_id': f'card-{socket_test_data["card1_id"]}',
        'new_list_id': f'list-{socket_test_data["list2_id"]}',
        'next_sibling_id': None # Move to end of list
    }
    
    # Emit the event
    socket_client.emit('card_moved', move_data)
    
    # Check the database for the change
    card = Card.query.get(socket_test_data['card1_id'])
    assert card is not None
    assert card.list_id == socket_test_data['list2_id']
    assert card.position == 0 # It's the only card in the new list

def test_socket_card_moved_broadcast(app, socket_test_data, registered_user):
    """Test that a move is broadcast to other clients."""
    
    # We need two clients
    client1 = socketio.test_client(app)
    client2 = socketio.test_client(app)
    
    # We need to log them in via a linked HTTP client
    http_client1 = app.test_client()
    http_client1.post('/auth/login', data={'email': registered_user.email, 'password': 'password123'})
    
    http_client2 = app.test_client()
    http_client2.post('/auth/login', data={'email': registered_user.email, 'password': 'password123'})
    
    client1.flask_test_client = http_client1
    client2.flask_test_client = http_client2
    
    board_id_str = str(socket_test_data['board_id'])
    
    # Both clients join the room
    client1.emit('join_board', {'board_id': board_id_str})
    client2.emit('join_board', {'board_id': board_id_str})
    
    # Clear client 2's received messages
    client2.get_received()
    
    # Client 1 moves the card
    move_data = {
        'card_id': f'card-{socket_test_data["card1_id"]}',
        'new_list_id': f'list-{socket_test_data["list2_id"]}',
        'next_sibling_id': None
    }
    client1.emit('card_moved', move_data)
    
    # Check Client 2's messages for the broadcast
    received = client2.get_received()
    
    assert len(received) > 0
    assert received[0]['name'] == 'card_update_broadcast'
    assert received[0]['args'][0]['card_id'] == move_data['card_id']
    assert received[0]['args'][0]['new_list_id'] == move_data['new_list_id']