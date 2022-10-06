"""Review model tests."""

import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Author, Category, Publisher, Book, Review

os.environ['DATABASE_URL'] = "postgresql:///booklyn-test"

from app import app

db.create_all()

class BookModelTestCase(TestCase):
    """Test models for reviews."""

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
        u1.currently_reading.append(new_book)
        u1.read.append(new_book)
        u1.favorite.append(new_book)
        db.session.commit()

        self.title = title

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    
    def test_review_model(self):
        """Does basic model work?"""

        book = Book.query.filter_by(title=self.title).first()
        user = User.query.get(self.u1_id)

        new_review = Review(rating=5, review='Loved it!', user_id=self.u1_id, book_id=book.id)
        db.session.add(new_review)
        db.session.commit()

        self.assertEqual(len(user.reviews), 1)
        self.assertEqual(user.reviews[0].rating, 5)
        self.assertEqual(user.reviews[0].review, 'Loved it!')
        self.assertEqual(len(book.reviews), 1)
        self.assertEqual(book.reviews[0].rating, 5)
        self.assertEqual(book.reviews[0].review, 'Loved it!')
