"""Review view tests."""

import os
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

        book = Book.query.filter_by(title=title).first()
        user = User.query.get(u1_id)

        rating = 5
        review = 'Loved it!'

        new_review = Review(rating=rating, review=review, user_id=u1_id, book_id=book1.id)
        db.session.add(new_review)
        db.session.commit()

        self.rating = rating
        self.review = review

    
    def test_show_reviews(self):
        """Test show_reviews."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.get(f'/users/{self.u1_id}/reviews')
            html = resp.get_data(as_text=True)

            self.assertIn(f'{self.rating}', html)
            self.assertIn(self.review, html)


    def test_show_book_post(self):
        """Test show_book view with post request."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.post(f'/books/{self.volumeId}', data={'rating': f'{self.rating}', 'review': self.review})

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, f'/books/{self.volumeId}')

    def test_show_book_post_redirection_followed(self):
        """Test redirection of show_book view with post request."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.post(f'/books/{self.volumeId}', data={'rating': f'{self.rating}', 'review': self.review}, follow_redirects=True)

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(f'{self.review}', html)

    def test_delete_review(self):
        """Test delete_review view."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            review = Review.query.filter_by(review=self.review).first()
            resp = c.post(f'/users/{self.u1_id}/reviews/{review.id}/delete')

            self.assertEqual(resp.status_code, 302)

    def test_delete_review_redirection_followed(self):
        """Test redirection of delete review view."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            review = Review.query.filter_by(review=self.review).first()
            resp = c.post(f'/users/{self.u1_id}/reviews/{review.id}/delete', follow_redirects=True)

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Reviews', html)


    def test_update_review_get(self):
        """Test update_review view with get request."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            review = Review.query.filter_by(review=self.review).first()
            resp = c.get(f'/users/{self.u1_id}/reviews/{review.id}/update')

            # user = User.query.get(self.u1_id)
            # print('*******************')
            # print(review, user.reviews)

            self.assertEqual(resp.status_code, 200)
            self.assertEqual(f'{review.review}', self.review)

    def test_update_review_post(self):
        """Test update_review view with post request."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id
            review = Review.query.filter_by(review=self.review).first()
            book = Book.query.filter_by(title=self.title).first()

            edit = 'Edited!'

            resp = c.post(f'/users/{self.u1_id}/reviews/{review.id}/update', data={
                review.rating : 3,
                review.review : 'Loved it',
                review.user_id : self.u1_id,
                review.book_id : book.id
            })

            db.session.commit()
            review.update_time()

            self.assertEqual(resp.status_code, 302)


    def test_update_review_post_redirection_followed(self):
        """Test redirection of update_review view with post request."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            review = Review.query.filter_by(review=self.review).first()
            book = Book.query.filter_by(title=self.title).first()

            resp = c.post(f'/users/{self.u1_id}/reviews/{review.id}/update', data={
                review.rating : 3,
                review.review : 'Loved it',
                review.user_id : self.u1_id,
                review.book_id : book.id
            }, follow_redirects=True)

            db.session.commit()
            review.update_time()

            html = resp.get_data(as_text=True)

            user = User.query.get(self.u1_id)
            print('*******************')
            print('review', user.reviews)

            self.assertEqual(resp.status_code, 200)
            # self.assertIn('Edited!', html)




            


            
