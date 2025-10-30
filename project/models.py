from project import db, login_manager
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    """Required callback for Flask-Login to load a user from session."""
    return User.query.get(int(user_id))

# --- NEW: Many-to-Many Association Table ---
# This table links Users and Boards (for membership)
board_members = db.Table('board_members',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('board_id', db.Integer, db.ForeignKey('boards.id'), primary_key=True)
)


class User(db.Model, UserMixin):
    """User model for authentication."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to Boards (one-to-many for *ownership*)
    # We rename this from 'boards' to 'owned_boards' for clarity
    owned_boards = db.relationship('Board', back_populates='owner', lazy=True, cascade="all, delete-orphan")

    # --- NEW: Many-to-Many Relationship for *membership* ---
    shared_boards = db.relationship('Board', secondary=board_members,
                                    back_populates='members', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.username}>'


class Board(db.Model):
    """Board model."""
    __tablename__ = 'boards'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationship back to the owner (User)
    owner = db.relationship('User', back_populates='owned_boards')
    
    # Relationship to Lists (one-to-many)
    lists = db.relationship('List', backref='board', lazy=True, cascade="all, delete-orphan",
                            order_by='List.position')
                            
    # --- NEW: Many-to-Many Relationship for *members* ---
    members = db.relationship('User', secondary=board_members,
                              back_populates='shared_boards', lazy='dynamic')


class List(db.Model):
    # ... (This model does not need any changes) ...
    __tablename__ = 'lists'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.Integer, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    board_id = db.Column(db.Integer, db.ForeignKey('boards.id'), nullable=False)
    
    cards = db.relationship('Card', backref='list', lazy=True, cascade="all, delete-orphan",
                            order_by='Card.position')


class Card(db.Model):
    # ... (This model does not need any changes) ...
    __tablename__ = 'cards'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    position = db.Column(db.Integer, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    list_id = db.Column(db.Integer, db.ForeignKey('lists.id'), nullable=False)