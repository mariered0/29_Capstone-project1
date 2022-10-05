"""Book model tests."""

import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Author, Category, Publisher, Book, Review

os.environ['DATABASE_URL'] = "postgresql:///booklyn-test"

from app import app

db.create_all()

class BookModelTestCase(TestCase):
    """Test models for books."""

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

    def test_book_model(self):
        """Does basic book model work?"""

        #Create data for a book

        #Create author data in db
        authors = ['Walter Isaacson']
        Author.create_author_data(authors)

        #Create category data in db
        categories = ['Biography & Autobiography']
        Category.create_category_data(categories)

        #Create publisher data in db
        publisher = 'Simon and Schuster'
        new_publisher = Publisher(publisher=publisher)
        db.session.add(new_publisher)
        db.session.commit()

        #Create book data in db
        volumeId = 'f_D3DwAAQBAJ'
        title = 'The Code Breaker'
        subtitle = 'Jennifer Doudna, Gene Editing, and the Future of the Human Race'
        thumbnail = "http://books.google.com/books/publisher/content?id=f_D3DwAAQBAJ&printsec=frontcover&img=1&zoom=1&edge=curl&imgtk=AFLRE70ogUC9thba4ywARMEUSeR3uP_056AnNzo_W4dtTLWITx96D5JgPkTpYgU1krF6vnyzQ4ZlpnEgNNM0BOWN13WzACnu8EEFnXP3tC_URDvkZyPLQbqJPWH9m16Lfz0ljM_R-SE0&source=gbs_api"

        publisher = Publisher.query.filter_by(publisher=publisher).first_or_404()

        new_book = Book.create_book_data(volumeId, title, subtitle, thumbnail, authors, categories, publisher)

        book = Book.query.filter_by(title=title).first()

        #The above book created should have the following author, title, category and publisher.
        self.assertEqual(len(book.authors), 1)
        self.assertEqual(book.title, 'The Code Breaker')
        self.assertEqual(book.categories[0].category, 'Biography & Autobiography')
        self.assertEqual(book.publisher.publisher, 'Simon and Schuster')
        self.assertEqual(book.volumeId, 'f_D3DwAAQBAJ')
        self.assertEqual(book.subtitle, 'Jennifer Doudna, Gene Editing, and the Future of the Human Race')
        self.assertEqual(book.thumbnail, 'http://books.google.com/books/publisher/content?id=f_D3DwAAQBAJ&printsec=frontcover&img=1&zoom=1&edge=curl&imgtk=AFLRE70ogUC9thba4ywARMEUSeR3uP_056AnNzo_W4dtTLWITx96D5JgPkTpYgU1krF6vnyzQ4ZlpnEgNNM0BOWN13WzACnu8EEFnXP3tC_URDvkZyPLQbqJPWH9m16Lfz0ljM_R-SE0&source=gbs_api')

    def test_book_model(self):
        """Can we add a book with same author as the sample data to db?"""

        #Create data for a book

        #Create author data in db
        authors = ['Malcolm Gladwell']
        Author.create_author_data(authors)

        #Create category data in db
        categories = ['Business & Economics']
        Category.create_category_data(categories)

        #Create publisher data in db
        publisher = 'Back Bay Books'
        new_publisher = Publisher(publisher=publisher)
        db.session.add(new_publisher)
        db.session.commit()

        #Create book data in db
        volumeId = 'VKGbb1hg8JAC'
        title = 'Blink'
        subtitle = 'The Power of Thinking Without Thinking'
        thumbnail = "http://books.google.com/books/content?id=VKGbb1hg8JAC&printsec=frontcover&img=1&zoom=1&edge=curl&imgtk=AFLRE72jj3LZtaGOCyGtjukGRgEOfxAr7Ughrw51wf8NDhRO4vJa6OdOozMvL9IOJ7Jb2LVQnhXE9WdCC5gMonEfdAarGzuR6AJ-QtRzyuI3Jk_uh0W5YFtlul66SEDarJmjE_q7jeRj&source=gbs_api"

        publisher = Publisher.query.filter_by(publisher=publisher).first_or_404()

        new_book = Book.create_book_data(volumeId, title, subtitle, thumbnail, authors, categories, publisher)

        book = Book.query.filter_by(title=title).first()

        self.assertEqual(len(book.authors), 1)
        self.assertEqual(book.authors[0].author, 'Malcolm Gladwell')
        self.assertEqual(book.title, title)
        self.assertEqual(book.categories[0].category, 'Business & Economics')
        self.assertEqual(book.publisher.publisher, 'Back Bay Books')
        self.assertEqual(book.volumeId, volumeId)
        self.assertEqual(book.subtitle, subtitle)
        self.assertEqual(book.thumbnail, thumbnail)



        

