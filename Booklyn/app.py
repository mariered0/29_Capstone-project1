from flask import Flask, request, render_template, redirect, flash, session, g
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

from forms import UserAddForm, LoginForm, UserEditForm, BookReviewForm
from secret import GOOGLE_BOOKS_API_KEY
from models import db, connect_db, User, Author, Publisher, Category, Book, Review
from werkzeug.datastructures import MultiDict

import requests, ast

CURR_USER_KEY = 'curr_user'

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///booklyn_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#this echo allows us to see the SQL lines that happen in background
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False


connect_db(app)

app.config['SECRET_KEY'] = "hahaha1987"
# app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

url = 'https://www.googleapis.com/books/v1'




@app.route('/search')
def search():
    """Get book data."""
    if not g.user:
        flash("Access unauthorized.", 'danger')
        return redirect('users/signup.html')

    user = g.user

    search = request.args.get('q')
        


    res = requests.get(f'{url}/volumes', params={'key': GOOGLE_BOOKS_API_KEY, 'q': search, 'maxResults':40} )
    result = res.json()
    
    # items = []

    # for book in result['items']:
    #     check = {}

    #     print('check values', check.values())
    #     if book['volumeInfo']['title'] not in check and book['volumeInfo']['authors'] not in check:
    #         check['title'] = {book['volumeInfo']['title']}
    #         check['author'] = book['volumeInfo']['authors']
    #         items.append({
    #             'title': book['volumeInfo']['title'], 
    #             'authors': book['volumeInfo']['authors'], 
    #             'publisher': book['volumeInfo']['publisher'], 
    #             'thubmnail': book['volumeInfo']['imageLinks']['thumbnail']})

    # print('result', items)


    return render_template('search_result.html', result=result, search=search, user=user)



###################################################################
# User signup/login/logout
###################################################################



@app.before_request
def add_user_to_g():
    """If logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
    else:
        g.user = None

def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id

def do_logout():
    """Logout user"""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/')
def home_page():
    """Show homepage."""

    user = g.user

    return render_template('home.html', user=user)


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.
    Create new user and add to DB. Redirect to home page.
    If home not valid, display form.
    """

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                image_url=form.image_url.data or User.image_url.default.arg
            )
            db.session.commit()

        except IntegrityError:
            flash("This username is already taken", 'danger')
            return render_template('users/signup.html', form=form)

        do_login(user)

        return redirect(f'/users/{user.id}/')
    else:
        return render_template('users/signup.html', form=form)

@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", 'success')
            return redirect('/')

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)

@app.route('/logout')
def logout():
    """Handle logout of user."""

    user = User.query.get(session[CURR_USER_KEY])
    do_logout()
    flash(f"Goodbye, {user.username}!", 'success')
    return redirect('/login')



##########################################################
# User - add to/remove from lists
##########################################################

@app.route('/users/<int:user_id>/add_want_to_read', methods=['POST'])
def add_want_to_read(user_id):
    """Add book to want_to_read list."""

    if not g.user:
        flash("Access unauthorized.", 'danger')
        return redirect('/')

    data = {}
    for key, value in request.form.items():
        print("item: {0}, data: {1}".format(key, value))
        data[key] = value
    
    # Create author data in db
    authors = ast.literal_eval(data['author'])

    User.create_author_data(authors)

    # Create category data in db
    if len(data['category']) is 0:
        categories = ['N/A']
    else:
        categories = ast.literal_eval(data['category'])

    User.create_category_data(categories)

    publisher = data['publisher']

    if not Publisher.query.filter(Publisher.publisher == publisher).first():
        new_publisher = Publisher(publisher=publisher)
        db.session.add(new_publisher)
        db.session.commit()

    # Create book data in db
    volumeId = data['volumeId']
    title = data['title']
    subtitle = data['subtitle']
    thumbnail = data['thumbnail']

    publisher = Publisher.query.filter_by(publisher=publisher).first()

    User.create_book_data(volumeId, title, subtitle, thumbnail, authors, categories, publisher)
    new_book = User.create_book_data(volumeId, title, subtitle, thumbnail, authors, categories, publisher)

    user = g.user

    # Add the relationship between book id and and user id to db
    user.want_to_read.append(new_book)
    db.session.commit()
    
    flash('Added to the list!', 'success')

    return redirect(f'/users/{user.id}/want_to_read')


@app.route('/users/<int:user_id>/want_to_read/<int:book_id>/delete', methods=['POST'])
def remove_want_to_read(user_id, book_id):
    """Remove the book from want_to_read list."""

    user = User.query.get_or_404(user_id)
    book = Book.query.get_or_404(book_id)
    user.want_to_read.remove(book)
    db.session.commit()

    return redirect(f'/users/{user.id}/want_to_read')


@app.route('/users/<int:user_id>/add_currently_reading', methods=['POST'])
def add_currently_reading(user_id):
    """Add book to currently_reading list."""

    if not g.user:
        flash("Access unauthorized.", 'danger')
        return redirect('/')

    data = {}
    for key, value in request.form.items():
        print("item: {0}, data: {1}".format(key, value))
        data[key] = value
    
    # Create author data in db
    authors = ast.literal_eval(data['author'])

    User.create_author_data(authors)

    # Create category data in db
    if len(data['category']) is 0:
        categories = ['N/A']
    else:
        categories = ast.literal_eval(data['category'])
    
    User.create_category_data(categories)

    publisher = data['publisher']
    if not Publisher.query.filter(Publisher.publisher == publisher).first():
        new_publisher = Publisher(publisher=publisher)
        db.session.add(new_publisher)
        db.session.commit()

    # Create book data in db
    volumeId = data['volumeId']
    title = data['title']
    subtitle = data['subtitle']
    thumbnail = data['thumbnail']

    publisher = Publisher.query.filter_by(publisher=publisher).first()

    User.create_book_data(volumeId, title, subtitle, thumbnail, authors, categories, publisher)
    new_book = User.create_book_data(volumeId, title, subtitle, thumbnail, authors, categories, publisher)

    user = g.user

    # Add the relationship between book id and and user id to db
    user.currently_reading.append(new_book)
    db.session.commit()
    
    flash('Added to the list!', 'success')

    return redirect(f'/users/{user.id}/currently_reading')


@app.route('/users/<int:user_id>/currently_reading/<int:book_id>/delete', methods=['POST'])
def remove_currently_reading(user_id, book_id):
    """Remove the book from currently_reading list."""

    user = User.query.get_or_404(user_id)
    book = Book.query.get_or_404(book_id)
    user.currently_reading.remove(book)
    db.session.commit()

    return redirect(f'/users/{user.id}/currently_reading')


@app.route('/users/<int:user_id>/add_read', methods=['POST'])
def add_read(user_id):
    """Add book to read list."""

    if not g.user:
        flash("Access unauthorized.", 'danger')
        return redirect('/')

    data = {}
    for key, value in request.form.items():
        print("item: {0}, data: {1}".format(key, value))
        data[key] = value
    
    # Create author data in db
    authors = ast.literal_eval(data['author'])

    User.create_author_data(authors)

    # Create category data in db
    if len(data['category']) is 0:
        categories = ['N/A']
    else:
        categories = ast.literal_eval(data['category'])

    User.create_category_data(categories)

    publisher = data['publisher']
    if not Publisher.query.filter(Publisher.publisher == publisher).first():
        new_publisher = Publisher(publisher=publisher)
        db.session.add(new_publisher)
        db.session.commit()

    # Create book data in db
    volumeId = data['volumeId']
    title = data['title']
    subtitle = data['subtitle']
    thumbnail = data['thumbnail']


    publisher = Publisher.query.filter_by(publisher=publisher).first()

    User.create_book_data(volumeId, title, subtitle, thumbnail, authors, categories, publisher)
    new_book = User.create_book_data(volumeId, title, subtitle, thumbnail, authors, categories, publisher)

    user = g.user

    # Add the relationship between book id and and user id to db
    print('new_book', new_book)
    user.read.append(new_book)
    db.session.commit()
    
    flash('Added to the list!', 'success')

    return redirect(f'/users/{user.id}/read')


@app.route('/users/<int:user_id>/read/<int:book_id>/delete', methods=['POST'])
def remove_read(user_id, book_id):
    """Remove the book from read list."""

    user = User.query.get_or_404(user_id)
    book = Book.query.get_or_404(book_id)
    user.read.remove(book)
    db.session.commit()

    return redirect(f'/users/{user.id}/read')

@app.route('/users/<int:user_id>/add_favorite', methods=['POST'])
def add_favorite(user_id):
    """Add book to favorite list."""

    if not g.user:
        flash("Access unauthorized.", 'danger')
        return redirect('/')

    data = {}
    for key, value in request.form.items():
        print("item: {0}, data: {1}".format(key, value))
        data[key] = value
    
    # Create author data in db
    authors = ast.literal_eval(data['author'])

    User.create_author_data(authors)

    # Create category data in db
    if len(data['category']) is 0:
        categories = ['N/A']
    else:
        categories = ast.literal_eval(data['category'])

    User.create_category_data(categories)

    publisher = data['publisher']
    if not Publisher.query.filter(Publisher.publisher == publisher).first():
        new_publisher = Publisher(publisher=publisher)
        db.session.add(new_publisher)
        db.session.commit()

    # Create book data in db
    volumeId = data['volumeId']
    title = data['title']
    subtitle = data['subtitle']
    thumbnail = data['thumbnail']

    publisher = Publisher.query.filter_by(publisher=publisher).first()

    User.create_book_data(volumeId, title, subtitle, thumbnail, authors, categories, publisher)
    new_book = User.create_book_data(volumeId, title, subtitle, thumbnail, authors, categories, publisher)

    user = g.user

    # Add the relationship between book id and and user id to db
    print('new_book', new_book)
    user.favorite.append(new_book)
    db.session.commit()
    
    flash('Added to the list!', 'success')

    return redirect(f'/users/{user.id}/favorite')


@app.route('/users/<int:user_id>/favorite/<int:book_id>/delete', methods=['POST'])
def remove_favorite(user_id, book_id):
    """Remove the book from favorite list."""

    user = User.query.get_or_404(user_id)
    book = Book.query.get_or_404(book_id)
    user.favorite.remove(book)
    db.session.commit()

    return redirect(f'/users/{user.id}/favorite')



##########################################################
# User
##########################################################

@app.route('/users/<int:user_id>')
def users_show(user_id):
    """Show user page."""
    user = User.query.get_or_404(user_id)

    return render_template('users/show.html', user=user)


@app.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
def user_edit(user_id):
    """Show user profile edit page."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect('/')

    user = User.query.get_or_404(user_id)
    form = UserEditForm()

    if form.validate_on_submit():

        if User.authenticate(user.username, form.password.data):

            user.username = form.username.data
            user.email = form.email.data
            user.image_url = form.image_url.data or '/static/images/user.png'
            user.bio = form.bio.data
            db.session.commit()

        flash('User profile has been edited!', 'success')
        return redirect(f'/users/{user.id}')
    else:
        return render_template(f'/users/edit.html', form=form, user=user)



@app.route('/users/<int:user_id>/want_to_read')
def show_want_to_read(user_id):
    """Show user's want_to_read list."""

    if not g.user:
        flash("Access unauthorized.", 'danger')
        return redirect('/')
    
    user = User.query.get_or_404(user_id)

    return render_template('users/lists/list_want_to_read.html', user=user)



@app.route('/users/<int:user_id>/currently_reading')
def show_currently_reading(user_id):
    """Show user's currently_reading list."""

    if not g.user:
        flash("Access unauthorized.", 'danger')
        return redirect('/')
    
    user = User.query.get_or_404(user_id)

    return render_template('users/lists/list_currently_reading.html', user=user)



@app.route('/users/<int:user_id>/read')
def show_read(user_id):
    """Show user's read list."""

    if not g.user:
        flash("Access unauthorized.", 'danger')
        return redirect('/')
    
    user = User.query.get_or_404(user_id)

    return render_template('users/lists/list_read.html', user=user)



@app.route('/users/<int:user_id>/favorite')
def show_favorite(user_id):
    """Show user's favorite list."""

    if not g.user:
        flash("Access unauthorized.", 'danger')
        return redirect('/')
    
    user = User.query.get_or_404(user_id)

    return render_template('users/lists/list_favorite.html', user=user)


@app.route('/users/<int:user_id>/review/<int:book_id>')
def write_review(user_id, book_id):
    """Show a page to write review for a book."""

    if not g.user:
        flash("Access unauthorized.", 'danger')
        return redirect('/')

    user = User.query.get_or_404(user_id)
    book = Book.query.get_or_404(book_id)
    form = BookReviewForm()

    if form.validate_on_submit():
        review = Review(user_id=user_id, book_id=book_id, rating=form.rating.data, review=form.review.data)
        db.session.commit()

        redirect('/')
    
    return render_template('/users/reviews/review.html', form=form)

    

    
    user = User.query.get_or_404(user_id)

    return render_template('/users/list_favorite.html', user=user)


##########################################################
# Book
##########################################################

@app.route('/books/<volumeId>', methods=['GET', 'POST'])
def show_book(volumeId):
    """Show book detail page with review form if the user already has the book in their list."""

    user = g.user
    # data = MultiDict(mapping=request.form)
    # form = BookReviewForm(data)
    form = BookReviewForm()

    res = requests.get(f'{url}/volumes/{volumeId}', params={'key': GOOGLE_BOOKS_API_KEY} )
    result = res.json()
    desc = result['volumeInfo']['description']

    book = Book.query.filter_by(volumeId=volumeId).first()

    if form.validate_on_submit():

        rating = form.rating.data
        review = form.review.data

        print('**************************')
        print('rating', rating)
        print('review', review)

        return redirect('/')



    else:
        print('not validated')



    if not book:
        return render_template('book.html', result=result, user=user, desc=desc)

    # if the book is in any of the lists for the user, show review form
    elif user.is_book_in_list(book.id):
        return render_template('book.html', result=result, user=user, desc=desc, form=form)

    

    


    

