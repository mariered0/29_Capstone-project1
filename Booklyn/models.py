"""SQLAlchemy models for Booklyn."""


from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

import ast

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

    def __repr__(self):
        return f"<Author #{self.id}: {self.author}>"

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
    subtitle = db.Column(db.Text, nullable=True)
    thumbnail = db.Column(db.Text, default='/static/images/cover-not-available.png')
    # published_date = db.Column(db.DateTime, nullable=False)

    publisher_id = db.Column(db.Integer, db.ForeignKey('publishers.id'), nullable=False)

    authors = db.relationship('Author', secondary='books_authors', backref='books')
    categories = db.relationship('Category', secondary='books_categories', backref='books')
    
    publisher = db.relationship('Publisher', backref='books', primaryjoin='Publisher.id==Book.publisher_id')

    def __repr__(self):
        return f"<Book #{self.id}: {self.title}, {self.authors}, {self.categories}>"


class BookAuthor(db.Model):
    """Middle table for the relationship between a book and authors."""

    __tablename__ = 'books_authors'

    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'), primary_key=True)


class BookCategory(db.Model):
    """Middle table for the relationship between a book and categories."""

    __tablename__ = 'books_categories'

    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), primary_key=True)


class WantToRead(db.Model):
    """Middle table for the relationship between a user and the user's want_to_read books."""

    __tablename__ = 'want_to_read'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="cascade"), primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id', ondelete="cascade"), primary_key=True)
    date_added = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    

class CurrentlyReading(db.Model):
    """Middle table for the relationship between a user and the books that the user's currently reading."""

    __tablename__ = 'currently_reading'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="cascade"), primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id', ondelete="cascade"), primary_key=True)
    date_added = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())


class Read(db.Model):
    """Middle table for the relationship between a user and the books that the user has read."""

    __tablename__ = 'read'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="cascade"), primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id', ondelete="cascade"), primary_key=True)
    date_added = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())


class Favorite(db.Model):
    """Middle table for the relationship between a user and their favorite books."""

    __tablename__ = 'favorite'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="cascade"), primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id', ondelete="cascade"), primary_key=True)
    date_added = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())


class User(db.Model):
    """Users."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False, unique=True)
    image_url = db.Column(db.Text, default='/static/images/user.png')
    bio = db.Column(db.Text, nullable=True)

    want_to_read = db.relationship('Book', secondary='want_to_read', backref='want_to_read_books')
    currently_reading = db.relationship('Book', secondary='currently_reading', backref='currently_reading_books')
    read = db.relationship('Book', secondary='read', backref='read_books')
    favorite = db.relationship('Book', secondary='favorite', backref='favorite_books')

    reviews = db.relationship('Review', backref='user')

    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"

    def want_to_read_imgs(self, user):
        """Images of books the user wants to read."""

        books = [book.thumbnail for book in user.want_to_read]
        print('thumbnails', books)
        return books;


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


    @classmethod
    def create_author_data(self, authors):
        """Check if the author data already exists in db, and if it doesn't, add the author data to db."""

        # if there are multiple authors
        if len(authors) != 1:
            for author in authors:
                if not Author.query.filter(Author.author == author).all():
                    new_author = Author(author=author)
                    db.session.add(new_author)
                    db.session.commit()

        # if there's only one author
        else:
            if not Author.query.filter(Author.author == authors[0]).all():
                new_author = Author(author=authors[0])
                db.session.add(new_author)
                db.session.commit()

    @classmethod
    def create_category_data(self, categories):
        """Check if the category data already exists in db, and if it doesn't, add the category data to db."""

        # if there are multiple categories
        if len(categories) != 1:
            for category in categories:
                if not Category.query.filter(Category.category == category).all():
                    new_category = Category(category=category)
                    db.session.add(new_category)
                    db.session.commit()

        #if there's only one category
        else:
            if not Category.query.filter(Category.category == categories[0]).all():
                new_category = Category(category=categories[0])
                db.session.add(new_category)
                db.session.commit()

    @classmethod
    def create_book_data(self, title, subtitle, thumbnail, authors, categories, publisher):
        """ """

        # Create book data in db
        publisher_id=publisher.id

        if not Book.query.filter_by(title=title).first():
            new_book = Book(title=title, subtitle=subtitle, thumbnail=thumbnail or User.thumbnail.default.arg, publisher_id=publisher_id)
            db.session.add(new_book)
            db.session.commit()

        # Create books_authors relationship
            if len(authors) != 1:
                for author in authors:
                    author = Author.query.filter(Author.author == author).first()
                    new_book.authors.append(author)
                    db.session.commit()
            else:
                author = Author.query.filter(Author.author == authors[0]).first()
                new_book.authors.append(author)
                db.session.commit()

        # Create books_categories relationship
            if len(categories) != 1:
                for category in categories:
                    cat = Category.query.filter(Category.category == category).first()
                    new_book.categories.append(cat)
                    db.session.commit()
            else:
                cat = Category.query.filter(Category.category == categories[0]).first()
                new_book.categories.append(cat)
                db.session.commit()

        else:
            new_book = Book.query.filter_by(title=title, publisher=publisher).first()

        return new_book
        



class Review(db.Model):
    """Reviews."""

    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    review = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    date_added = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    





    



