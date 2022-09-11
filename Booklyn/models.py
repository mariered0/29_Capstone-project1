"""SQLAlchemy models for Booklyn."""

# from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

def connect_db(app):
    """Connect to database."""
    db.app = app
    db.init_app(app)
    



class Category(db.Model):
    """Categories for books."""

    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.Text, nullable=False)

class Author(db.Model):
    """Authors for books."""

    __tablename__ = 'authors'

    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.Text, nullable=False)

class Publisher(db.Model):
    """Publishers for books."""

    __tablename__ = 'publishers'

    id = db.Column(db.Integer, primary_key=True)
    publisher = db.Column(db.Text, nullable=False)
  

class Book(db.Model):
    """Books."""

    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    subtitle = db.Column(db.Text, nullable=False)
    thumbnail = db.Column(db.Text, default='/static/images/cover-not-available.png')
    published_date = db.Column(db.DateTime, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    publisher_id = db.Column(db.Integer, db.ForeignKey('publishers.id'), nullable=False)

    
    publisher = db.relationship('Publisher', backref='books', primaryjoin='Publisher.id==Book.publisher_id')
    authors = db.relationship('Author', backref='books')

    book_want_to_read = db.relationship("User", backref='user_want_to_read', primaryjoin='User.want_to_read==Book.id')
    book_currently_reading = db.relationship("User", backref='user_currently_reading', primaryjoin='User.currently_reading==Book.id')
    book_have_read = db.relationship("User", backref='user_have_read', primaryjoin='User.have_read==Book.id')
    book_favorite = db.relationship("User", backref='user_favorite', primaryjoin='User.favorite==Book.id')

class User(db.Model):
    """Users."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False, unique=True)
    image_url = db.Column(db.Text, default='/static/images/user.png')
    bio = db.Column(db.Text, nullable=True)
    want_to_read = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=True)
    currently_reading = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=True)
    have_read = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=True)
    favorite = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=True)

    
    reviews = db.relationship('Review', backref='user')

    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"

    @classmethod
    def signup(cls, username, password, email, image_url):
        """Sing up user."""

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
            image_url=image_url,
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with username and password"""

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user
    
        return False



class Review(db.Model):
    """Reviews."""

    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    review = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    





    



