from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from project.models import User

# --- USER FORMS (From Module 1) ---

class RegistrationForm(FlaskForm):
    """Form for user registration."""
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        """Check if username is already taken."""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        """Check if email is already in use."""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already in use. Please choose a different one.')


class LoginForm(FlaskForm):
    """Form for user login."""
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


# --- MODULE 2: NEW FORMS ---

class CreateBoardForm(FlaskForm):
    """Form to create a new board."""
    name = StringField('Board Name', validators=[DataRequired(), Length(min=3, max=100)])
    submit = SubmitField('Create Board')

class CreateListForm(FlaskForm):
    """Form to create a new list."""
    name = StringField('List Name', validators=[DataRequired(), Length(min=1, max=100)])
    submit = SubmitField('Create List')

class CreateCardForm(FlaskForm):
    """Form to create a new card."""
    title = StringField('Card Title', validators=[DataRequired(), Length(min=1, max=200)])
    description = TextAreaField('Description (Optional)', validators=[Length(max=500)])
    submit = SubmitField('Create Card')

# --- NEW: Board Sharing Form ---

class InviteUserForm(FlaskForm):
    """Form to invite a user to a board by email."""
    email = StringField('User Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Invite User')

    def validate_email(self, email):
        """Check if user exists."""
        user = User.query.filter_by(email=email.data).first()
        if not user:
            raise ValidationError('No user found with that email address.')