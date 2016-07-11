import uuid

from datetime import datetime, timedelta
from houraiteahouse.app import bcrypt, db
from sqlalchemy.orm import backref

# Database model class definitions

# Sec 0: Static definitions & dependencies

# Establish the secondary object for the News Tags many-to-many relationship.
tags = db.Table('tags',
    db.Column('tag_id', db.Integer, db.ForeignKey('newstag.tag_id'), nullable=False),
    db.Column('news_id', db.Integer, db.ForeignKey('news.post_id'), nullable=False)
)


# Sec 1: User AuthN & AuthZ        

# User authN & metadata
class User(db.Model):    
    __tablename__ = "user"
    
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(64), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    permissions_id = db.Column(db.Integer, db.ForeignKey('permissions.permissions_id'), nullable=False)
    permissions = db.relationship('UserPermissions', backref=db.backref('user', lazy='dynamic'))
    # TODO: user registration confirmation
    
    def __init__(self, email, username, password, permissions):
        self.email = email
        self.username = username
        self.password = bcrypt.generate_password_hash(password)
        self.permissions = permissions
        self.registered_on = datetime.now()
        
    def change_password(self, password):
        self.password = bcrypt.generate_password_hash(password)
        
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)
    
    def is_active(self):
        return True
    
    def get_id(self):
        return self.user_id
    
    def get_permissions(self):
        return self.permissions
    
    def __repr__(self):
        return '<User {0}>'.format(self.email)
    
# Session tracking
class UserSession(db.Model):
    __tablename__ = "sessions"
    
    session_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    session_uuid = db.Column(db.String(36), nullable=False, unique=True)
    valid_after = db.Column(db.DateTime, nullable=False)
    valid_before = db.Column(db.DateTime, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    user = db.relationship('User', backref=db.backref('session', lazy='dynamic'))
    
    def __init__(self, user, remember_me=False):
        self.user = user
        self.valid_after = datetime.now() # Prevent time travel
        if remember_me:
            self.valid_before = None
        else:
            self.valid_before = datetime.now() + timedelta(days=1)
        
    def is_valid(self):
        now = datetime.now()
        return self.valid_after < now and self.valid_before > now
    
    def get_user(self):
        return self.user
    
    def get_id(self):
        return self.session_id
        
    def get_uuid(self):
        return self.session_uuid
    
    def __repr__(self):
        return '<UserSession {0}>'.format(self.session_uuid)

# User authZ
class UserPermissions(db.Model):
    __tablename__ = "permissions"
    
    permissions_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    master = db.Column(db.Boolean, nullable=False, default=False) # Someone with host & DB access. Admins cannot change their permissions. This can only be set manually.
    admin = db.Column(db.Boolean, nullable=False, default=False) # User administrative rights - can edit people's permissions
    team = db.Column(db.Boolean, nullable=False, default=False) # User is a member of our team.  They hyave access to our internal tools, but not necessarily every action.
    wiki = db.Column(db.Boolean, nullable=False, default=False) # Permission to edit Wiki pages
    news = db.Column(db.Boolean, nullable=False, default=False) # Permission to post news
    comment = db.Column(db.Boolean, nullable=False, default=True) # Permission to comment on news.  Can be revoked.

    def __init(self, admin=False, team=False, wiki=False, news=False, comment=True):
        self.admin = admin
        self.team = team
        self.wiki = wiki
        self.news = news
        self.comment = comment
        
    def get_id(self):
        return self.permissions_id


# Sec 2: News, tags, comments

# A news post.
class NewsPost(db.Model):
    __tablename__ = "news"
    
    post_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(120), nullable=False, unique=True)
    body = db.Column(db.String(65535), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
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
        return self.post_id
    
    def __repr__(self):
        return '<NewsPost {0}>'.format(self.title)


# Tags for news. Many-to-many.
class NewsTag(db.Model):
    __tablename__ = "newstag"
    
    tag_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), nullable=False, unique=True)
    news = db.relationship('NewsPost', secondary=tags, back_populates="tags")
    
    def __init__(self, name):
        self.name = name
    
    def get_id(self):
        return self.tag_id
    
    def __repr__(self):
        return '<NewsTag {0}>'.format(self.name)


# Comments on a news post.  Many-to-one.
class NewsComment(db.Model):
    __tablename__ = "newscomment"
    
    comment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    body = db.Column(db.String(65535), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    author = db.relationship('User',
        backref=db.backref('newscomment', lazy='dynamic'))
    news_id = db.Column(db.Integer, db.ForeignKey('news.post_id'), nullable=False)
    news = db.relationship('NewsPost',
        backref=db.backref('newscomment', lazy='dynamic'))
    
    def __init__(self, body, author, news):
        self.body = body
        self.author = author
        self.news = news

    def get_id(self):
        return self.comment_id
