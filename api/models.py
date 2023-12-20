from datetime import datetime
from .app import db

class Student(db.Model):

    id = db.Column(db.Integer, primary_key=True, )
    email = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=False)
    display_name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.strptime('2016-11-08 22:18:03','%Y-%m-%d %H:%M:%S'))
    started_at = db.Column(db.Date, nullable=False, default=datetime.strptime('2016-11-08','%Y-%m-%d'))
