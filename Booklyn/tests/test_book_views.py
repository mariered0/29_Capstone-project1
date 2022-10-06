"""Book view tests."""

import os, requests
from unittest import TestCase

from models import db, connect_db, User, Author, Category, Publisher, Book, Review
from secret import GOOGLE_BOOKS_API_KEY


os.environ['DATABASE_URL'] = "postgresql:///booklyn-test"

from app import app, CURR_USER_KEY

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False



class BookViewTestCase(TestCase):
    """Test views for book."""

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
        book1 = Book.query.filter_by(title=title).first()

        #Add the relationship with the book above and a user
        u1.want_to_read.append(book1)
        u1.currently_reading.append(book1)
        u1.read.append(book1)
        u1.favorite.append(book1)
        db.session.commit()

        self.title = title
        self.volumeId = volumeId

    def test_search(self):
        """Test search view."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            search = 'blink'
            url = 'https://www.googleapis.com/books/v1'

            res = requests.get(f'{url}/volumes', params={'key': GOOGLE_BOOKS_API_KEY, 'q': search, 'maxResults':5, 'printType': 'books'} )

            resp = c.get(f'/search?q={search}', )
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Blink", html)
            self.assertIn("Blink!", html)
            self.assertIn("I Miss You When I Blink", html)

    def test_show_book_get(self):
        """Test show_book view with get request."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            url = 'https://www.googleapis.com/books/v1'

            res = requests.get(f'{url}/volumes/{self.volumeId}', params={'key': GOOGLE_BOOKS_API_KEY} )
            result = res.json()

            resp = c.get(f'/books/{self.volumeId}', )
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(self.title, html)




            