from flask import Flask, request, render_template, redirect, flash, session, g
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

from forms import UserAddForm, LoginForm
from secret import GOOGLE_BOOKS_API_KEY
from models import db, connect_db, User, Author, Publisher, Category, Book, BookAuthor, BookCategory, Review, WantToRead, CurrentlyReading, Read, Favorite

import requests, ast

CURR_USER_KEY = 'curr_user'

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///booklyn_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#this echo allows us to see the SQL lines that happen in background
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False


connect_db(app)

app.config['SECRET_KEY'] = "hahaha1987"
# app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

url = 'https://www.googleapis.com/books/v1'




@app.route('/search')
def search():
    """Get book data."""
    search = request.args.get('q')
    # print(GOOGLE_BOOKS_API_KEY)
    res = requests.get(f'{url}/volumes', params={'key': GOOGLE_BOOKS_API_KEY, 'q': search} )
    result = res.json()
    # print('result', result)
    return render_template('search_result.html', result=result, search=search)



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
    return render_template('home.html')


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

        return redirect('/')
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
# Books
##########################################################


@app.route('/users/add_want_to_read', methods=['POST'])
def add_want_to_read():
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

    # if there are multiple authors
    if len(authors) != 1:
        for author in authors:
            if not Author.query.filter(Author.author == author).all():
                print('went through author')
                new_author = Author(author=author)
                db.session.add(new_author)
                db.session.commit()

    # if there's only one author
    else:
        if not Author.query.filter(Author.author == authors[0]).all():
                print('went through author else')
                new_author = Author(author=authors[0])
                db.session.add(new_author)
                db.session.commit()

    # Create category data in db
    categories = ast.literal_eval(data['category'])
    print('categories', categories[0])
    if len(categories) != 1:
        for category in categories:
            if not Category.query.filter(Category.category == category).all():
                print('went through category')
                new_category = Category(category=category)
                db.session.add(new_category)
                db.session.commit()
    else:
        if not Category.query.filter(Category.category == categories[0]).all():
            print('went through category else')
            new_category = Category(category=categories[0])
            print('category', categories[0])
            db.session.add(new_category)
            db.session.commit()

    publisher = data['publisher']
    if not Publisher.query.filter(Publisher.publisher == publisher).all():
        new_publisher = Publisher(publisher=publisher)
        print('went through publisher')
        db.session.add(new_publisher)
        db.session.commit()

    # Create book data in db
    title = data['title']
    subtitle = data['subtitle']
    thumbnail = data['thumbnail']

    publisher = Publisher.query.filter_by(publisher=publisher).first()
    publisher_id = publisher.id

    if not Book.query.filter_by(title=title).first():
        print('went through book')
        new_book = Book(title=title, subtitle=subtitle, thumbnail=thumbnail, publisher_id=publisher_id)
        db.session.add(new_book)
        db.session.commit()

        # Create books_authors relationship
        if len(authors) != 1:
            for author in authors:
                author = Author.query.filter(Author.author == author).first()
                print('author to add', author)
                new_book.authors.append(author)
                db.session.commit()
        else:
            author = Author.query.filter(Author.author == authors[0]).first()
            print('author to add', author)
            new_book.authors.append(author)
            db.session.commit()

        # Create books_categories relationship
        if len(categories) != 1:
            for category in categories:
                cat = Category.query.filter(Category.category == category).first()
                print('category to add', cat)
                new_book.categories.append(cat)
                db.session.commit()
        else:
            cat = Category.query.filter(Category.category == categories[0]).first()
            print('category to add', cat)
            new_book.categories.append(cat)
            db.session.commit()

    else:
        new_book = Book.query.filter_by(title=title, publisher=publisher).first()

    user = g.user
    print('g.user', g.user)

    user.want_to_read.append(new_book)
    db.session.commit()
    
    flash('Added to the list!', 'success')

    return redirect('/')


##########################################################
# Users
##########################################################

@app.route('/users/<int:user_id>')
def users_show(user_id):
    """Show user page."""
    user = User.query.get_or_404(user_id)

    return render_template('users/show.html', user=user)
