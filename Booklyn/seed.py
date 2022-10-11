"""Seed file to make sample data for db."""

from models import db
from app import app


# Create all tables
with app.app_context():
    db.drop_all()
    db.create_all()