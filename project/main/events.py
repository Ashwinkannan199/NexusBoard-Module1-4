from flask import request
from flask_socketio import emit, join_room, leave_room
from project import socketio, db
from project.models import Card, List, Board # Import Board
from flask_login import current_user # Import current_user
from sqlalchemy import and_

@socketio.on('join_board')
def handle_join_board(data):
    """
    Client emits this event when they load a board page.
    This adds them to a 'room' for that specific board.
    """
    board_id = data['board_id']
    board = Board.query.get(int(board_id))

    # --- NEW: Socket Security Check ---
    if not current_user.is_authenticated or (board.owner != current_user and current_user not in board.members.all()):
        print(f"Unauthorized socket join attempt for board {board_id}")
        return # Do not let them join the room

    join_room(board_id)
    print(f"Client {request.sid} joined board {board_id}")


@socketio.on('leave_board')
def handle_leave_board(data):
    # ... (This function is fine, no security check needed to leave) ...
    board_id = data['board_id']
    leave_room(board_id)
    print(f"Client {request.sid} left board {board_id}")


@socketio.on('card_moved')
def handle_card_move(data):
    """
    Fired when a user drags and drops a card.
    Updates the database and broadcasts the change to other users.
    """
    try:
        # Parse data from client
        card_id_int = int(data['card_id'].split('-')[1])
        new_list_id_int = int(data['new_list_id'].split('-')[1])
        
        card = Card.query.get_or_404(card_id_int)
        
        # --- NEW: Socket Security Check ---
        board = card.list.board
        if not current_user.is_authenticated or (board.owner != current_user and current_user not in board.members.all()):
            print(f"Unauthorized socket move attempt by {current_user.id} for board {board.id}")
            emit('move_error', {'error': 'You do not have permission to modify this board.'}, room=request.sid)
            return

        # --- (Rest of the function is the same as Module 4) ---
        
        next_sibling_id_str = data['next_sibling_id']
        board_id = board.id # Get board_id for broadcasting
        
        old_list_id_int = card.list_id
        old_position = card.position

        # Calculate new position
        new_position = 0
        if next_sibling_id_str:
            sibling_id_int = int(next_sibling_id_str.split('-')[1])
            sibling = Card.query.get_or_404(sibling_id_int)
            new_position = sibling.position
        else:
            new_position = db.session.query(db.func.count(Card.id)).filter(
                Card.list_id == new_list_id_int
            ).scalar()
            if old_list_id_int == new_list_id_int and old_position < new_position:
                 new_position -= 1

        # Database Update Transaction
        if old_list_id_int == new_list_id_int:
            if old_position < new_position:
                # Moving Down
                db.session.query(Card).filter(
                    Card.list_id == old_list_id_int,
                    Card.position > old_position,
                    Card.position <= new_position
                ).update({'position': Card.position - 1}, synchronize_session=False)
            else:
                # Moving Up
                db.session.query(Card).filter(
                    Card.list_id == old_list_id_int,
                    Card.position >= new_position,
                    Card.position < old_position
                ).update({'position': Card.position + 1}, synchronize_session=False)
        else:
            # Move to a different list
            db.session.query(Card).filter(
                Card.list_id == old_list_id_int,
                Card.position > old_position
            ).update({'position': Card.position - 1}, synchronize_session=False)
            db.session.query(Card).filter(
                Card.list_id == new_list_id_int,
                Card.position >= new_position
            ).update({'position': Card.position + 1}, synchronize_session=False)

        card.list_id = new_list_id_int
        card.position = new_position
        db.session.commit()
        
        # Broadcast the change
        emit('card_update_broadcast', data, room=str(board_id), skip_sid=request.sid)

    except Exception as e:
        db.session.rollback()
        print(f"Error handling card move: {e}")
        emit('move_error', {'error': str(e)}, room=request.sid)