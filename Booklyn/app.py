from flask import Flask, request, render_template, redirect, flash
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy
from secret import GOOGLE_BOOKS_API_KEY
from models import db, connect_db, User

import requests


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///booklyn_db'

db = SQLAlchemy()


connect_db(app);

app.config['SECRET_KEY'] = "hahaha1987"
# app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

url = 'https://www.googleapis.com/books/v1'

@app.route('/')
def home_page():
    """Show homepage."""
    return render_template('home.html')


@app.route('/search')
def search():
    """Get book data."""
    search = request.args.get('q')
    print(GOOGLE_BOOKS_API_KEY)
    res = requests.get(f'{url}/volumes', params={'key': GOOGLE_BOOKS_API_KEY, 'q': search} )
    result = res.json()
    print('result', result)
    return render_template('search_result.html', result=result, search=search)





