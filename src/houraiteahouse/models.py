import time
import uuid
from datetime import datetime, timedelta
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref
import code

bcrypt = Bcrypt()
db = SQLAlchemy()

# Database model class definitions

# Sec 0: Static definitions & dependencies

# Establish the secondary object for the News Tags many-to-many relationship.
tags = db.Table('tags',
    db.Column('tag_id', db.Integer, db.ForeignKey('newstag.tag_id'), nullable=False),
    db.Column('news_id', db.Integer, db.ForeignKey('news.post_id'), nullable=False)
)


# Language codes
class Language(db.Model):
    __tablename__ = "languages"
    
    language_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    language_code = db.Column(db.String(3), nullable=False)
    language_name = db.Column(db.String(50))
    
    def __init__(self, code, name):
        self.language_code = code
        self.language_name = name
        
    def get_id(self):
        return self.language_id
        
    def get_language_code(self):
        return self.language_code
    
    def get_language_name(self):
        return self.language_name


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
        self.registered_on = datetime.utcnow()
        
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
    
    def get_username(self):
        return self.username
    
    def __repr__(self):
        return '<User {0}>'.format(self.username)
    
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
        self.session_uuid = str(uuid.uuid4())
        self.valid_after = datetime.utcnow() # Prevent time travel
        if remember_me:
            self.valid_before = None
        else:
            self.valid_before = datetime.utcnow() + timedelta(days=1)
            
    def get_expiration(self):
        return None if self.valid_before is None else int(time.mktime(self.valid_before.timetuple())) * 1000
        
    def is_valid(self):
        now = datetime.utcnow()
        if self.valid_before is not None and self.valid_before < now:
            return False
        return self.valid_after < now
    
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
    master = db.Column(db.Boolean, nullable=False, default=False) # Someone with host & DB access. admins cannot change a master's permissions. This can only be set manually.  Equivalent of "webmaster"
    admin = db.Column(db.Boolean, nullable=False, default=False) # User administrative rights - can edit people's permissions.  Only masters can set this.  Essential moderator powers/etc.
    team = db.Column(db.Boolean, nullable=False, default=False) # User is a member of our team.  They have access to our internal tools, but not necessarily every action.
    wiki = db.Column(db.Boolean, nullable=False, default=False) # Permission to edit Wiki pages
    news = db.Column(db.Boolean, nullable=False, default=False) # Permission to post news (specifical new posts
    translate = db.Column(db.Boolean, nullable=False, default=False) # Permission to translate existing content.  Does not allow new posting, etc
    comment = db.Column(db.Boolean, nullable=False, default=True) # Permission to comment on news.  Can be revoked.

    def __init(self, admin=False, team=False, wiki=False, news=False, comment=True):
        self.admin = admin
        self.team = team
        self.wiki = wiki
        self.news = news
        self.comment = comment
        
    def get_id(self):
        return self.permissions_id
    
    def update_permissions(self, newPermissions):
        for permType, value in newPermissions.items():
            if getattr(self, permType) != value:
                if permType == 'master':
                    raise Exception('Master can only be set manually!')
                setattr(self, permType, value)


# Sec 2: News, tags, comments

# A news post.
class NewsPost(db.Model):
    __tablename__ = "news"
    
    post_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post_short = db.Column(db.String(64), nullable=False, unique=True)
    media = db.Column(db.String(1024)) # If someone tries to post a media URL > 1024 chars I will end them
    author_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    created = db.Column(db.DateTime, nullable=False)
    author = db.relationship('User',
        backref=db.backref('newspost', lazy='dynamic'))
    comments = db.relationship('NewsComment',
        backref=db.backref('newspost'))
    tags = db.relationship('NewsTag', secondary=tags, back_populates="news")
    lastEdit = db.Column(db.DateTime, nullable=True)
    
    def __init__(self, short, title, created, author, tags, media=None):
        self.post_short = short
        self.title = title
        self.created = created
        self.author = author
        self.tags = tags
        self.media = media
    
    def get_id(self):
        return self.post_id
    
    def get_short(self):
        return self.post_short
    
    def get_author(self):
        return self.author
    
    def __repr__(self):
        return '<NewsPost {0}>'.format(self.title)


# Localized news titles. Many-to-one.
class NewsTitle(db.Model):
    __tablename__ = "newstitle"
    
    news_id = db.Column(db.Integer, db.ForeignKey('news.post_id'), nullable=False, primary_key=True)
    news = db.relationship('NewsPost',
        backref=db.backref('newstitle', lazy='dynamic'))
    language_id = db.Column(db.Integer, db.ForeignKey('languages.language_id'), nullable=False, primary_key=True)
    language = db.relationship('Language',
        backref=db.backref('newstitle', lazy='dynamic'))
    localized_title = db.Column(db.String(1000))
    
    def __init__(self, news, language, title):
        self.news = news
        self.language = language
        self.localized_title = title
        
    def get_title(self):
        return self.localized_title
    

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
    body = db.Column(db.String(10000), nullable=False) # Don't ask about the exact #. It's a mysql bug.
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
    
    def get_author(self):
        return self.author
