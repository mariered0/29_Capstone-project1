from ast import Pass
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField
from wtforms.validators import InputRequired, Email, Length, AnyOf



class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[InputRequired()])
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
    image_url = StringField('(Optional) Image URL')

class LoginForm(FlaskForm):
    """Form for login users."""

    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])

class UserEditForm(FlaskForm):
    """Form for editing users."""

    username = StringField('Username', validators=[InputRequired()])
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
    image_url = StringField('(Optional) Image URL')
    bio = TextAreaField('Bio', validators=[Length(max=500)])

class BookReviewForm(FlaskForm):
    """Form for book reviews."""

    rating = SelectField('Rating', choices=[('1', '1'), ('2', '2'), ('3','3'), ('4','4'), ('5', '5')], validators=[AnyOf(values=['1', '2', '3', '4', '5'])])
    review = TextAreaField('(Optional) Review', validators=[Length(max=500)])

