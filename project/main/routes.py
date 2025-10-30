from flask import render_template, redirect, url_for, flash, abort, request
from flask_login import login_required, current_user
from . import main
from project import db
from project.models import User, Board, List, Card
from project.forms import CreateBoardForm, CreateListForm, CreateCardForm, InviteUserForm

@main.route("/")
@main.route("/index")
def index():
    """Serves the homepage."""
    return render_template('index.html')


@main.route("/dashboard", methods=['GET', 'POST'])
@login_required  # This protects the route
def dashboard():
    """
    Serves the main dashboard page.
    Handles display of user's boards and creation of new boards.
    """
    form = CreateBoardForm()
    
    # Handle new board creation
    if form.validate_on_submit():
        board_name = form.name.data
        new_board = Board(name=board_name, owner=current_user)
        db.session.add(new_board)
        db.session.commit()
        flash('New board created!', 'success')
        return redirect(url_for('main.dashboard'))
    
    # --- UPDATED: Fetch both owned and shared boards ---
    owned_boards = Board.query.filter_by(user_id=current_user.id).order_by(Board.date_created.desc()).all()
    shared_boards = current_user.shared_boards.order_by(Board.date_created.desc()).all()
    
    return render_template('dashboard.html', title='Dashboard', form=form, 
                           owned_boards=owned_boards, shared_boards=shared_boards)


@main.route("/board/<int:board_id>")
@login_required
def view_board(board_id):
    """
    Displays a specific board, its lists, and its cards.
    """
    board = Board.query.get_or_404(board_id)
    
    # --- UPDATED: Security Check ---
    # User must be the owner OR a member to view
    if board.owner != current_user and current_user not in board.members:
        abort(403) # Forbidden

    list_form = CreateListForm()
    card_form = CreateCardForm()
    
    return render_template('board.html', title=board.name, board=board, 
                           list_form=list_form, card_form=card_form)

# --- CRUD Routes for Lists ---

@main.route("/list/create/<int:board_id>", methods=['POST'])
@login_required
def create_list(board_id):
    board = Board.query.get_or_404(board_id)
    
    # --- UPDATED: Security Check ---
    if board.owner != current_user and current_user not in board.members:
        abort(403)
        
    form = CreateListForm()
    if form.validate_on_submit():
        # ... (rest of function is unchanged)
        list_name = form.name.data
        position = len(board.lists)
        new_list = List(name=list_name, board_id=board.id, position=position)
        db.session.add(new_list)
        db.session.commit()
        flash('List created!', 'success')
    else:
        flash('Error creating list.', 'danger')
        
    return redirect(url_for('main.view_board', board_id=board.id))


@main.route("/list/delete/<int:list_id>", methods=['POST'])
@login_required
def delete_list(list_id):
    list_to_delete = List.query.get_or_404(list_id)
    board_id = list_to_delete.board_id
    
    # --- UPDATED: Security Check ---
    if list_to_delete.board.owner != current_user and current_user not in list_to_delete.board.members:
        abort(403)
    
    # ... (rest of function is unchanged)
    lists = List.query.filter(List.board_id == board_id, List.position > list_to_delete.position).all()
    for list_item in lists:
        list_item.position -= 1

    db.session.delete(list_to_delete)
    db.session.commit()
    flash('List deleted.', 'success')
    return redirect(url_for('main.view_board', board_id=board_id))

# --- CRUD Routes for Cards ---

@main.route("/card/create/<int:list_id>", methods=['POST'])
@login_required
def create_card(list_id):
    list_item = List.query.get_or_404(list_id)
    
    # --- UPDATED: Security Check ---
    if list_item.board.owner != current_user and current_user not in list_item.board.members:
        abort(403)
        
    form = CreateCardForm()
    if form.validate_on_submit():
        # ... (rest of function is unchanged)
        card_title = form.title.data
        card_desc = form.description.data
        position = len(list_item.cards)
        new_card = Card(title=card_title, description=card_desc, 
                        list_id=list_item.id, position=position)
        db.session.add(new_card)
        db.session.commit()
        flash('Card created!', 'success')
    else:
        flash('Error creating card.', 'danger')

    return redirect(url_for('main.view_board', board_id=list_item.board_id))


@main.route("/card/delete/<int:card_id>", methods=['POST'])
@login_required
def delete_card(card_id):
    card_to_delete = Card.query.get_or_404(card_id)
    board_id = card_to_delete.list.board_id
    
    # --- UPDATED: Security Check ---
    if card_to_delete.list.board.owner != current_user and current_user not in card_to_delete.list.board.members:
        abort(403)

    # ... (rest of function is unchanged)
    list_id = card_to_delete.list_id
    cards = Card.query.filter(Card.list_id == list_id, Card.position > card_to_delete.position).all()
    for card in cards:
        card.position -= 1

    db.session.delete(card_to_delete)
    db.session.commit()
    flash('Card deleted.', 'success')
    return redirect(url_for('main.view_board', board_id=board_id))

# --- CRUD Routes for Board (Owner-Only) ---
# We are LEAVING the security checks as-is for delete/edit board,
# as only the OWNER should be able to do this.

@main.route("/board/delete/<int:board_id>", methods=['POST'])
@login_required
def delete_board(board_id):
    board_to_delete = Board.query.get_or_404(board_id)
    
    # --- UNCHANGED: Only owner can delete ---
    if board_to_delete.owner != current_user:
        abort(403)
    
    db.session.delete(board_to_delete)
    db.session.commit()
    flash('Board deleted.', 'success')
    return redirect(url_for('main.dashboard'))


@main.route("/board/edit/<int:board_id>", methods=['GET', 'POST'])
@login_required
def edit_board(board_id):
    board = Board.query.get_or_404(board_id)
    
    # --- UNCHANGED: Only owner can edit ---
    if board.owner != current_user:
        abort(403)
        
    form = CreateBoardForm()
    if form.validate_on_submit():
        # ... (rest of function is unchanged)
        board.name = form.name.data
        db.session.commit()
        flash('Board has been updated!', 'success')
        return redirect(url_for('main.dashboard'))
    elif request.method == 'GET':
        form.name.data = board.name
        
    return render_template('edit_board.html', title='Edit Board', form=form, board=board)

# --- Edit routes for List/Card (Member Access) ---

@main.route("/list/edit/<int:list_id>", methods=['GET', 'POST'])
@login_required
def edit_list(list_id):
    list_item = List.query.get_or_404(list_id)
    
    # --- UPDATED: Security Check ---
    if list_item.board.owner != current_user and current_user not in list_item.board.members:
        abort(403)
        
    form = CreateListForm()
    if form.validate_on_submit():
        # ... (rest of function is unchanged)
        list_item.name = form.name.data
        db.session.commit()
        flash('List has been updated!', 'success')
        return redirect(url_for('main.view_board', board_id=list_item.board_id))
    elif request.method == 'GET':
        form.name.data = list_item.name
        
    return render_template('edit_list.html', title='Edit List', form=form, list=list_item)


@main.route("/card/edit/<int:card_id>", methods=['GET', 'POST'])
@login_required
def edit_card(card_id):
    card = Card.query.get_or_404(card_id)
    
    # --- UPDATED: Security Check ---
    if card.list.board.owner != current_user and current_user not in card.list.board.members:
        abort(403)
        
    form = CreateCardForm()
    if form.validate_on_submit():
        # ... (rest of function is unchanged)
        card.title = form.title.data
        card.description = form.description.data
        db.session.commit()
        flash('Card has been updated!', 'success')
        return redirect(url_for('main.view_board', board_id=card.list.board_id))
    elif request.method == 'GET':
        form.title.data = card.title
        form.description.data = card.description
        
    return render_template('edit_card.html', title='Edit Card', form=form, card=card)


# --- NEW: Board Member Management Routes ---

@main.route("/board/<int:board_id>/manage", methods=['GET', 'POST'])
@login_required
def manage_board_members(board_id):
    """
    Page for the board owner to invite/remove members.
    """
    board = Board.query.get_or_404(board_id)
    
    # --- Security: ONLY owner can manage members ---
    if board.owner != current_user:
        abort(403)
        
    form = InviteUserForm()
    
    if form.validate_on_submit():
        try:
            user_to_invite = User.query.filter_by(email=form.email.data).first()
            if user_to_invite == current_user:
                flash('You cannot invite yourself.', 'warning')
            elif user_to_invite in board.members:
                flash(f'{user_to_invite.username} is already a member.', 'info')
            else:
                board.members.append(user_to_invite)
                db.session.commit()
                flash(f'Invited {user_to_invite.username} to the board.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {e}', 'danger')
        return redirect(url_for('main.manage_board_members', board_id=board.id))

    # GET request:
    # Get all members (using .all() here to pass the list to the template)
    members = board.members.all()
    return render_template('manage_board.html', title="Manage Members", board=board, form=form, members=members)


@main.route("/board/<int:board_id>/remove_member/<int:user_id>", methods=['POST'])
@login_required
def remove_member(board_id, user_id):
    """
    Removes a member from a board.
    """
    board = Board.query.get_or_404(board_id)
    user_to_remove = User.query.get_or_404(user_id)
    
    # --- Security: ONLY owner can remove members ---
    if board.owner != current_user:
        abort(403)
    
    if user_to_remove not in board.members:
        flash(f'{user_to_remove.username} is not a member of this board.', 'warning')
    else:
        try:
            board.members.remove(user_to_remove)
            db.session.commit()
            flash(f'Removed {user_to_remove.username} from the board.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {e}', 'danger')
            
    return redirect(url_for('main.manage_board_members', board_id=board.id))