import uuid

from datetime import datetime
from houraiteahouse.app import bcrypt, db

tags = db.Table('tags',
    db.Column('tag_id', db.Integer, db.ForeignKey('newstag.id'), nullable=False),
    db.Column('news_id', db.Integer, db.ForeignKey('news.id'), nullable=False)
)


class NewsPost(db.Model):
    __tablename__ = "news"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(120), nullable=False, unique=True)
    body = db.Column(db.String(65535), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created = db.Column(db.DateTime, nullable=False)
    author = db.relationship('User',
        backref=db.backref('newspost', lazy='dynamic'))
    comments = db.relationship('NewsComment',
        backref=db.backref('newspost'))
    tags = db.relationship('NewsTag', secondary=tags, back_populates="news")
    
    def __init__(self, title, body, author, tags):
        self.title = title
        self.body = body
        self.created = datetime.now()
        self.author = author
        self.tags = tags
    
    def get_id(self):
        return self.id
    
    def __repr__(self):
        return '<NewsPost {0}>'.format(self.title)


class NewsTag(db.Model):
    __tablename__ = "newstag"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), nullable=False, unique=True)
    news = db.relationship('NewsPost', secondary=tags, back_populates="tags")
    
    def __init__(self, name):
        self.name = name
    
    def get_id(self):
        return self.id
    
    def __repr__(self):
        return '<NewsTag {0}>'.format(self.name)


class NewsComment(db.Model):
    __tablename__ = "newscomment"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    body = db.Column(db.String(65535), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship('User',
        backref=db.backref('newscomment', lazy='dynamic'))
    news_id = db.Column(db.Integer, db.ForeignKey('news.id'), nullable=False)
    news = db.relationship('NewsPost',
        backref=db.backref('newscomment', lazy='dynamic'))
    
    def __init__(self, body, author, news):
        self.body = body
        self.author = author
        self.news = news


class User(db.Model):
    
    __tablename__ = "user"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(64), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    
    def __init__(self, email, username, password, admin=False):
        self.email = email
        self.username = username
        self.password = bcrypt.generate_password_hash(password)
        self.registered_on = datetime.now()
        self.admin = admin
    
    def is_authenticated(self):
        return True
    
    def is_active(self):
        return True
    
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return self.id
    
    def __repr__(self):
        return '<User {0}>'.format(self.email)
