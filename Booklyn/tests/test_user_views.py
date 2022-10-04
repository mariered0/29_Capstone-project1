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
        book1 = Book.query.filter_by(title=title).first()

        #Add the relationship with the book above and a user
        u1.want_to_read.append(book1)
        u1.currently_reading.append(book1)
        u1.read.append(book1)
        u1.favorite.append(book1)
        db.session.commit()

        self.title = title


        ########################### - book2

        #Create author data in db
        authors2 = ['Tara Westover']
        Author.create_author_data(authors2)

        #Create category data in db
        categories2 = ['Biography & Autobiography']
        Category.create_category_data(categories2)

        #Create publisher data in db
        publisher2 = 'Random House'
        new_publisher = Publisher(publisher=publisher2)
        db.session.add(new_publisher)
        db.session.commit()

        #Create book data in db
        volumeId2 = '2ObWDgAAQBAJ'
        title2 = 'Educated'
        subtitle2 = 'A Memoir'
        thumbnail2 = "http://books.google.com/books/publisher/content?id=2ObWDgAAQBAJ&printsec=frontcover&img=1&zoom=1&edge=curl&imgtk=AFLRE70xRV9QCxXWGZT5riKLhEFXYIXcO-buPydg9timS8731-B6bTJO6DrEP77enBMim9ywnb27nkmb8XGTpiPc7lRkB6fxguM5YsJuAvS5BpUJdOr5xfg-rV0xhpDZ_AqeJg7F5vLh&source=gbs_api"


        book2 = Book.create_book_data(volumeId2, title2, subtitle2, thumbnail2, authors2, categories2, new_publisher)

        self.title2 = title2

        ########################## - book 3

        # Create author data in db
        authors3 = ['Malcolm Gladwell']
        Author.create_author_data(authors2)

        #Create category data in db
        categories3 = ['Business & Economics']
        Category.create_category_data(categories3)

        #Create publisher data in db
        publisher3 = 'Back Bay Books'
        new_publisher3 = Publisher(publisher=publisher3)
        db.session.add(new_publisher3)
        db.session.commit()

        #Create book data in db
        volumeId3 = 'VKGbb1hg8JAC'
        title3 = 'Blink'
        subtitle3 = 'The Power of Thinking Without Thinking'
        thumbnail3 = "http://books.google.com/books/content?id=VKGbb1hg8JAC&printsec=frontcover&img=1&zoom=1&edge=curl&imgtk=AFLRE73dS2bdhPK607ST7FNoaWbz_u_PEZY1hTXDQRC101FPPL6riCwQQzWPA2SE1kQlFr-Z-LUwPeMmJKiArOJfQ6PiRhz_qIbMBo_4zvpRDVFwmW1ggRVqbznMKfgsUjPunvuI9fMs&source=gbs_api"

        publisher = Publisher.query.filter_by(publisher=publisher3).first()

        book3 = Book.create_book_data(volumeId3, title3, subtitle3, thumbnail3, authors3, categories3, publisher)

        self.volumeId3 = volumeId3
        self.authors3 = authors3
        self.categories3 = categories3
        self.title3 = title3
        self.subtitle3 = subtitle3
        self.thumbnail3 = thumbnail3
        self.publisher3 = publisher3

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

#######################
#Lists
#######################

#Want_to_read list

    def test_add_want_to_read(self):
        """Test add_want_to_read view."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u2_id
            resp = c.post(f'/users/{self.u2_id}/add_want_to_read',
            data={
                'volumeId': self.volumeId3,
                'author': f'{self.authors3}',
                'publisher': self.publisher3,
                'category': f'{self.categories3}',
                'title': self.title3,
                'subtitle': self.subtitle3,
                'thumbnail': self.thumbnail3
            })

            user = User.query.get(self.u2_id)
            new_book = Book.query.filter_by(title=f'{self.title3}').first()

            #add book to want_to_read list
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
                'volumeId': self.volumeId3,
                'author': f'{self.authors3}',
                'publisher': self.publisher3,
                'category': f'{self.categories3}',
                'title': self.title3,
                'subtitle': self.subtitle3,
                'thumbnail': self.thumbnail3
                }, follow_redirects=True)

            user = User.query.get(self.u2_id)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)

            #Checking if the book added to the list is shown in show_want_to_read view.
            self.assertIn(f'{self.title3}', html)
            self.assertIn(f'{self.authors3[0]}', html)


    def test_show_want_to_read(self):
        """Test show_want_to_read view."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id
            resp = c.get(f'/users/{self.u1_id}/want_to_read')

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)

            self.assertIn(f'{self.title}', html)

#Currently reading list

    def test_add_currently_reading(self):
        """Test add_currently_reading view."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u2_id
            resp = c.post(f'/users/{self.u2_id}/add_currently_reading',
            data={
                'volumeId': self.volumeId3,
                'author': f'{self.authors3}',
                'publisher': self.publisher3,
                'category': f'{self.categories3}',
                'title': self.title3,
                'subtitle': self.subtitle3,
                'thumbnail': self.thumbnail3
            })

            user = User.query.get(self.u2_id)
            new_book = Book.query.filter_by(title=f'{self.title3}').first()

            #add book to currently_reading list
            user.currently_reading.append(new_book)
            db.session.commit()

            self.assertEqual(resp.status_code, 302)

            # Checking redirect
            self.assertEqual(resp.location, f"/users/{user.id}/currently_reading")


    def test_add_currenly_reading_redirection_followed(self):
        """Check the redirection from the above."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u2_id
            resp = c.post(f'/users/{self.u2_id}/add_currently_reading',
            data={
                'volumeId': self.volumeId3,
                'author': f'{self.authors3}',
                'publisher': self.publisher3,
                'category': f'{self.categories3}',
                'title': self.title3,
                'subtitle': self.subtitle3,
                'thumbnail': self.thumbnail3
                }, follow_redirects=True)

            user = User.query.get(self.u2_id)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)

            #Checking if the book added to the list is shown in show_currently_reading view.
            self.assertIn(f'{self.title3}', html)
            self.assertIn(f'{self.authors3[0]}', html)


    def test_show_currently_reading(self):
        """Test show_currently_reading view."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id
            resp = c.get(f'/users/{self.u1_id}/currently_reading')

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)

            self.assertIn(f'{self.title}', html)

#Read list

    def test_add_read(self):
        """Test add_read view."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u2_id
            resp = c.post(f'/users/{self.u2_id}/add_read',
            data={
                'volumeId': self.volumeId3,
                'author': f'{self.authors3}',
                'publisher': self.publisher3,
                'category': f'{self.categories3}',
                'title': self.title3,
                'subtitle': self.subtitle3,
                'thumbnail': self.thumbnail3
            })

            user = User.query.get(self.u2_id)
            new_book = Book.query.filter_by(title=f'{self.title3}').first()

            #add book to read list
            user.read.append(new_book)
            db.session.commit()

            self.assertEqual(resp.status_code, 302)

            # Checking redirect
            self.assertEqual(resp.location, f"/users/{user.id}/read")


    def test_add_read_redirection_followed(self):
        """Check the redirection from the above."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u2_id
            resp = c.post(f'/users/{self.u2_id}/add_read',
            data={
                'volumeId': self.volumeId3,
                'author': f'{self.authors3}',
                'publisher': self.publisher3,
                'category': f'{self.categories3}',
                'title': self.title3,
                'subtitle': self.subtitle3,
                'thumbnail': self.thumbnail3
                }, follow_redirects=True)

            user = User.query.get(self.u2_id)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)

            #Checking if the book added to the list is shown in show_read view.
            self.assertIn(f'{self.title3}', html)
            self.assertIn(f'{self.authors3[0]}', html)


    def test_show_read(self):
        """Test show_read view."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id
            resp = c.get(f'/users/{self.u1_id}/read')

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)

            self.assertIn(f'{self.title}', html)

#Favorite list

    def test_add_favorite(self):
        """Test add_favorite view."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u2_id
            resp = c.post(f'/users/{self.u2_id}/add_favorite',
            data={
                'volumeId': self.volumeId3,
                'author': f'{self.authors3}',
                'publisher': self.publisher3,
                'category': f'{self.categories3}',
                'title': self.title3,
                'subtitle': self.subtitle3,
                'thumbnail': self.thumbnail3
            })

            user = User.query.get(self.u2_id)
            new_book = Book.query.filter_by(title=f'{self.title3}').first()

            #add book to favorite list
            user.favorite.append(new_book)
            db.session.commit()

            self.assertEqual(resp.status_code, 302)

            # Checking redirect
            self.assertEqual(resp.location, f"/users/{user.id}/favorite")


    def test_add_favorite_redirection_followed(self):
        """Check the redirection from the above."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u2_id
            resp = c.post(f'/users/{self.u2_id}/add_favorite',
            data={
                'volumeId': self.volumeId3,
                'author': f'{self.authors3}',
                'publisher': self.publisher3,
                'category': f'{self.categories3}',
                'title': self.title3,
                'subtitle': self.subtitle3,
                'thumbnail': self.thumbnail3
                }, follow_redirects=True)

            user = User.query.get(self.u2_id)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)

            #Checking if the book added to the list is shown in show_favorite view.
            self.assertIn(f'{self.title3}', html)
            self.assertIn(f'{self.authors3[0]}', html)


    def test_show_favorite(self):
        """Test show_favorite view."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id
            resp = c.get(f'/users/{self.u1_id}/read')

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)

            self.assertIn(f'{self.title}', html)

    def test_remove_want_to_read(self):
        """Test remove_want_to_read view."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id
            book = Book.query.filter_by(title=self.title).first()
            resp = c.post(f'/users/{self.u1_id}/want_to_read/{book.id}/delete')

            user = User.query.get(self.u1_id)
            self.assertEqual(resp.status_code, 302)

            # Checking redirect
            self.assertEqual(resp.location, f"/users/{user.id}/want_to_read")

    def test_remove_want_to_read_redirection_followed(self):
        """Test redirection of the above view."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id
            book = Book.query.filter_by(title=self.title).first()
            resp = c.post(f'/users/{self.u1_id}/want_to_read/{book.id}/delete', follow_redirects=True)
            html = resp.get_data(as_text=True)

            user = User.query.get(self.u1_id)
           
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Want to Read', html)
            self.assertIn(f'{user.username}', html)

    def test_remove_currently_reading(self):
        """Test remove_currently_reading view."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id
            book = Book.query.filter_by(title=self.title).first()
            resp = c.post(f'/users/{self.u1_id}/currently_reading/{book.id}/delete')

            user = User.query.get(self.u1_id)
            self.assertEqual(resp.status_code, 302)

            # Checking redirect
            self.assertEqual(resp.location, f"/users/{user.id}/currently_reading")

    def test_remove_currently_reading_redirection_followed(self):
        """Test redirection of the above view."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id
            book = Book.query.filter_by(title=self.title).first()
            resp = c.post(f'/users/{self.u1_id}/currently_reading/{book.id}/delete', follow_redirects=True)
            html = resp.get_data(as_text=True)

            user = User.query.get(self.u1_id)
           
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Currently Reading', html)
            self.assertIn(f'{user.username}', html)


    def test_remove_read(self):
        """Test remove_read view."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id
            book = Book.query.filter_by(title=self.title).first()
            resp = c.post(f'/users/{self.u1_id}/read/{book.id}/delete')

            user = User.query.get(self.u1_id)
            self.assertEqual(resp.status_code, 302)

            # Checking redirect
            self.assertEqual(resp.location, f"/users/{user.id}/read")

    def test_remove_read_redirection_followed(self):
        """Test redirection of the above view."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id
            book = Book.query.filter_by(title=self.title).first()
            resp = c.post(f'/users/{self.u1_id}/read/{book.id}/delete', follow_redirects=True)
            html = resp.get_data(as_text=True)

            user = User.query.get(self.u1_id)
           
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Read', html)
            self.assertIn(f'{user.username}', html)


    def test_remove_favorite(self):
        """Test remove_favorite view."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id
            book = Book.query.filter_by(title=self.title).first()
            resp = c.post(f'/users/{self.u1_id}/favorite/{book.id}/delete')

            user = User.query.get(self.u1_id)
            self.assertEqual(resp.status_code, 302)

            # Checking redirect
            self.assertEqual(resp.location, f"/users/{user.id}/favorite")

    def test_remove_favorite_redirection_followed(self):
        """Test redirection of the above view."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id
            book = Book.query.filter_by(title=self.title).first()
            resp = c.post(f'/users/{self.u1_id}/favorite/{book.id}/delete', follow_redirects=True)
            html = resp.get_data(as_text=True)

            user = User.query.get(self.u1_id)
           
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Favorite', html)
            self.assertIn(f'{user.username}', html)

    






            




        


        

    
