# """User view tests."""

import os
from unittest import TestCase

from models import db, connect_db, User, Author, Category, Publisher, Book, Review
# from flask import current_app

os.environ['DATABASE_URL'] = "postgresql:///booklyn-test"

from app import app, CURR_USER_KEY

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False



class UserViewTestCase(TestCase):
    """Test views for users."""

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

        ########################### - book 1

        #Create author data in db
        authors1 = ['Tara Westover']
        Author.create_author_data(authors1)

        #Create category data in db
        categories1 = ['Biography & Autobiography']
        Category.create_category_data(categories1)

        #Create publisher data in db
        publisher1 = 'Random House'
        new_publisher = Publisher(publisher=publisher1)
        db.session.add(new_publisher)
        db.session.commit()

        #Create book data in db
        volumeId1 = '2ObWDgAAQBAJ'
        title1 = 'Educated'
        subtitle1 = 'A Memoir'
        thumbnail1 = "http://books.google.com/books/publisher/content?id=2ObWDgAAQBAJ&printsec=frontcover&img=1&zoom=1&edge=curl&imgtk=AFLRE70xRV9QCxXWGZT5riKLhEFXYIXcO-buPydg9timS8731-B6bTJO6DrEP77enBMim9ywnb27nkmb8XGTpiPc7lRkB6fxguM5YsJuAvS5BpUJdOr5xfg-rV0xhpDZ_AqeJg7F5vLh&source=gbs_api"


        Book.create_book_data(volumeId1, title1, subtitle1, thumbnail1, authors1, categories1, new_publisher)

        ########################## - book 2

        # Create author data in db
        authors2 = ['Malcolm Gladwell']
        Author.create_author_data(authors2)

        #Create category data in db
        categories2 = ['Business & Economics']
        Category.create_category_data(categories2)

        #Create publisher data in db
        publisher2 = 'Back Bay Books'
        new_publisher2 = Publisher(publisher=publisher2)
        db.session.add(new_publisher2)
        db.session.commit()

        #Create book data in db
        volumeId2 = 'VKGbb1hg8JAC'
        title2 = 'Blink'
        subtitle2 = 'The Power of Thinking Without Thinking'
        thumbnail2 = "http://books.google.com/books/content?id=VKGbb1hg8JAC&printsec=frontcover&img=1&zoom=1&edge=curl&imgtk=AFLRE73dS2bdhPK607ST7FNoaWbz_u_PEZY1hTXDQRC101FPPL6riCwQQzWPA2SE1kQlFr-Z-LUwPeMmJKiArOJfQ6PiRhz_qIbMBo_4zvpRDVFwmW1ggRVqbznMKfgsUjPunvuI9fMs&source=gbs_api"

        publisher = Publisher.query.filter_by(publisher=publisher2).first()

        Book.create_book_data(volumeId2, title2, subtitle2, thumbnail2, authors2, categories2, publisher)
        book_2 = Book.create_book_data(volumeId2, title2, subtitle2, thumbnail2, authors2, categories2, publisher)

        self.volumeId2 = volumeId2
        self.authors2 = authors2
        self.categories2 = categories2
        self.title2 = title2
        self.subtitle2 = subtitle2
        self.thumbnail2 = thumbnail2
        self.publisher2 = publisher2

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_home_page(self):
        """Test home page view."""

        with self.client as c:
            resp = c.get('/')

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Booklyn', str(resp.data))
            self.assertIn('search', str(resp.data))
    
    def test_users_show(self):
        """Test users_show (user profile) view."""

        with self.client as c:
            resp = c.get(f'/users/{self.u1_id}')

            self.assertEqual(resp.status_code, 200)
            self.assertIn("test1", str(resp.data))
            self.assertIn("bookshelves", str(resp.data))

    def test_users_edit(self):
        """Test users_edit view."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id
            resp = c.get(f'/users/{self.u1_id}/edit')


            self.assertEqual(resp.status_code, 200)
            self.assertIn("Edit Profile", str(resp.data))
            self.assertIn("test1", str(resp.data))
            self.assertIn("Bio", str(resp.data))

########################
# Lists
########################


    def test_add_want_to_read(self):
        """Test add_want_to_read view."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u2_id
            resp = c.post(f'/users/{self.u2_id}/add_want_to_read',
            data={
                'volumeId': self.volumeId2,
                'author': f'{self.authors2}',
                'publisher': self.publisher2,
                'category': f'{self.categories2}',
                'title': self.title2,
                'subtitle': self.subtitle2,
                'thumbnail': self.thumbnail2
            })

            html = resp.get_data(as_text=True)

            user = User.query.get(self.u2_id)
            new_book = Book.query.filter_by(title=f'{self.title2}').first()

            user.want_to_read.append(new_book)
            db.session.commit()

            self.assertEqual(resp.status_code, 302)

            # Checking redirect
            self.assertEqual(resp.location, f"/users/{user.id}/want_to_read")


    def test_add_want_to_read_redirection_followed(self):
        """Check the redirection from the above."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u2_id
            resp = c.post(f'/users/{self.u2_id}/add_want_to_read',
            data={
                'volumeId': self.volumeId2,
                'author': f'{self.authors2}',
                'publisher': self.publisher2,
                'category': f'{self.categories2}',
                'title': self.title2,
                'subtitle': self.subtitle2,
                'thumbnail': self.thumbnail2
                }, follow_redirects=True)

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)


    def test_add_want_to_read_with_new_book(self):
        """Test add_want_to_read view with new book."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u2_id
            resp = c.post(f'/users/{self.u2_id}/add_want_to_read',
            data={
                'volumeId': 'YY45EAAAQBAJ',
                'author': '['Stephen King']',
                'publisher': 'Hachette UK',
                'category': '['Fiction']',
                'title': 'The Body',
                'subtitle': None,
                'thumbnail': self.thumbnail2
            })

            html = resp.get_data(as_text=True)

            user = User.query.get(self.u2_id)
            new_book = Book.query.filter_by(title=f'{self.title2}').first()

            user.want_to_read.append(new_book)
            db.session.commit()

            self.assertEqual(resp.status_code, 302)

            # Checking redirect
            self.assertEqual(resp.location, f"/users/{user.id}/want_to_read")







            




        


        

    
