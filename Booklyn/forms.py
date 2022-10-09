from ast import Pass
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, RadioField
from wtforms.validators import InputRequired, Email, Length, AnyOf



class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('username', validators=[InputRequired()])
    email = StringField('email', validators=[InputRequired(), Email()])
    password = PasswordField('password', validators=[Length(min=6)])
    image_url = StringField('(optional) image url')

class LoginForm(FlaskForm):
    """Form for login users."""

    username = StringField('username', validators=[InputRequired()])
    password = PasswordField('password', validators=[Length(min=6)])

class UserEditForm(FlaskForm):
    """Form for editing users."""

    username = StringField('username', validators=[InputRequired()])
    email = StringField('email', validators=[InputRequired(), Email()])
    password = PasswordField('password', validators=[Length(min=6)])
    image_url = StringField('(optional) Image URL')
    bio = TextAreaField('bio', validators=[Length(max=500)])

class BookReviewForm(FlaskForm):
    """Form for book reviews."""

    rating = SelectField('rating', choices=[('1', '1'), ('2', '2'), ('3','3'), ('4','4'), ('5', '5')], validators=[AnyOf(values=['1', '2', '3', '4', '5'])])
    review = TextAreaField('(optional) review', validators=[Length(max=500)])

