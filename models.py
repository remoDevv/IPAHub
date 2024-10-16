from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy.sql import func

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    is_admin = db.Column(db.Boolean, default=False)
    apps = db.relationship('App', backref='author', lazy='dynamic')
    reviews = db.relationship('Review', backref='user', lazy='dynamic')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class App(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    icon_path = db.Column(db.String(255))
    file_path = db.Column(db.String(255))
    ios_version = db.Column(db.String(50))
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reports = db.relationship('Report', backref='app', lazy='dynamic')
    reviews = db.relationship('Review', backref='app', lazy='dynamic')
    average_rating = db.Column(db.Float, default=0.0)

    def __init__(self, **kwargs):
        super(App, self).__init__(**kwargs)

    def update_average_rating(self):
        avg = db.session.query(func.avg(Review.rating)).filter(Review.app_id == self.id).scalar()
        self.average_rating = round(avg, 2) if avg else 0.0
        db.session.commit()

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reason = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    app_id = db.Column(db.Integer, db.ForeignKey('app.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __init__(self, **kwargs):
        super(Report, self).__init__(**kwargs)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    app_id = db.Column(db.Integer, db.ForeignKey('app.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __init__(self, **kwargs):
        super(Review, self).__init__(**kwargs)
