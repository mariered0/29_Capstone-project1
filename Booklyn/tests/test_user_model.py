"""User model tests."""

import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Author, Category, Publisher, Book

os.environ['DATABASE_URL'] = "postgresql:///booklyn-test"

from app import app

db.create_all()

class UserModelTestCase(TestCase):
    """Test models for users."""

    def setUp(self):
        """Create test client, add sample data."""
        
        db.drop_all()
        db.create_all()

        #Setting up user 1 and 2.
        u1 = User.signup(username='test1', email='u1@gmail.com', password='password', image_url=None)
        u1_id = 1111
        u1.id = u1_id

        u2 = User.signup(username='test2', email='u2@gmail.com', password='password', image_url=None)
        u2_id = 2222
        u2.id = u2_id

        db.session.commit()

        u1 = User.query.get(u1_id)
        u2 = User.query.get(u2_id)

        self.u1 = u1
        self.u1_id = u1_id
        
        self.u2 = u2
        self.u2_id = u2_id

        self.client = app.test_client()

        ########################################
        #Create data for a book

        #Create author data in db
        authors = ['Malcolm Gladwell']
        Author.create_author_data(authors)

        #Create category data in db
        categories = ['Psychology']
        Category.create_category_data(categories)

        #Create publisher data in db
        publisher = 'Penguin UK'
        new_publisher = Publisher(publisher=publisher)
        db.session.add(new_publisher)
        db.session.commit()

        #Create book data in db
        volumeId = 'ialrgIT41OAC'
        title = 'Outliers'
        subtitle = 'The Story of Success'
        thumbnail = "http://books.google.com/books/content?id=ialrgIT41OAC&printsec=frontcover&img=1&zoom=1&edge=curl&imgtk=AFLRE72w989WrrTHWdOReyHMNFPdkySlbrf6TlmCvIAoYKeGFpCGACuhuW6MTYht3YT5lGZO9umWjPp3DKFDBIdMndmlXUDPLR-O11K0fHqMutXMl-FPraikyT9OL_GmFpqjGSu6mN5J&source=gbs_api"

        publisher = Publisher.query.filter_by(publisher=publisher).first_or_404()

        Book.create_book_data(volumeId, title, subtitle, thumbnail, authors, categories, publisher)
        new_book = Book.create_book_data(volumeId, title, subtitle, thumbnail, authors, categories, publisher)

        #Add the relationship with the book above and a user
        u1.want_to_read.append(new_book)
        db.session.commit()

        self.title = title


    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res


    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            username="testuser",
            email='test@gmail.com',
            password='password'
        )

        db.session.add(u)
        db.session.commit()

        # User should have 0 books in their lists & reviews
        self.assertEqual(len(u.favorite), 0)
        self.assertEqual(len(u.want_to_read), 0)
        self.assertEqual(len(u.currently_reading), 0)
        self.assertEqual(len(u.read), 0)
        self.assertEqual(len(u.reviews), 0)

    def test_valid_signup(self):
        """Does User.signup create a new user with valid credential?"""

        u = User.signup(
            username='testuser', 
            email='test@gmail.com',
            password='password',
            image_url=None)
        id = 3333
        u.id = id
        db.session.commit()

        u = User.query.get(id)
        self.assertIsNotNone(u)

        self.assertEqual(u.username, 'testuser')
        self.assertEqual(u.email, 'test@gmail.com')
        self.assertEqual(u.image_url, '/static/images/user.png')
        #This should be False because of hashing
        self.assertNotEqual(u.password, 'password')
        #Bcrypt strings start with this    
        self.assertTrue(u.password.startswith('$2b$'))

    def test_invalid_username_signup(self):
        """Does User.signup not create a new user with invalid username?"""

        u = User.signup(
            username=None, 
            email="test@test.com", 
            password="password",
            image_url=None)

        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_email_signup(self):
        """Does User.signup not create a new user with invalid email?"""

        u = User.signup(
            username='testuser', 
            email=None, 
            password="password",
            image_url=None)

        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()


    def test_invalid_password_signup(self):
        """Does User.signup not create a new user with invalid password?
        Password needs to have 6 characters or more."""

        with self.assertRaises(ValueError) as context:
            u = User.signup(
            username='testuser', 
            email='test@gmail.com', 
            password="",
            image_url=None)

        with self.assertRaises(ValueError) as context:
            u = User.signup(
            username='testuser', 
            email='test@gmail.com', 
            password=None,
            image_url=None)
    
    def test_valid_authentication(self):
        
        u = User.authenticate(self.u1.username, 'password')
        self.assertIsNotNone(u)
        self.assertEqual(u.id, self.u1_id)

    def test_invalid_authentication(self):
        self.assertFalse(User.authenticate(username='abc', password='password'))


    def test_wrong_password(self):
        """Does User.authenticate with incorrect password using the user, u1 return false? The correct password is password."""

        self.assertFalse(User.authenticate(username='test1', password='pass'))

    def test_is_book_in_list(self):
        """Does the is_book_in_list instance method function correctly?"""

        book = Book.query.filter_by(title=self.title).first()
        self.assertTrue(self.u1.is_book_in_list(book.id))


    def user_reviewed(self):
        """Does the user_reviewed instance method function correctly?"""

        book = Book.query.filter_by(title=self.title).first()
        self.assertFalse(self.u1.user_reviewed(book.id))


    

    


        





