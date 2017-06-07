import time
import uuid
from datetime import datetime, timedelta
from flask_bcrypt import Bcrypt
from flask_cache import Cache
from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy_cache import CachingQuery, FromCache
from sqlalchemy.orm import backref

bcrypt = Bcrypt()
db = SQLAlchemy(session_options={'query_cls': CachingQuery})
cache = Cache()

# Database model class definitions

# Sec 0: Static definitions & dependencies

# Establish the secondary object for the News Tags many-to-many relationship.
tags = db.Table(
    'tags',
    db.Column(
        'tag_id',
        db.Integer,
        db.ForeignKey('newstag.tag_id'),
        nullable=False),
    db.Column(
        'news_id',
        db.Integer,
        db.ForeignKey('news.post_id'),
        nullable=False))


def IdMixin(id_type=db.Integer):
    class _IdMixin(object):
        _id = db.Column('id', id_type, primary_key=True, autoincrement=True)

        @property
        def id(self):
            return self._id

    return _IdMixin


class HouraiTeahouseModel(db.Model):

    @classmethod
    def get(cls, *args, **kwargs):
        return cls.query.filter_by(*args, **kwargs).options(
            FromCache(cache)).first()

    @classmethod
    def get_or_die(cls, *args, **kwargs):
        entity = cls.get(*args, **kwargs)
        if entity is None:
            raise RuntimeError(
                'Entity %s with parameters "%s, %s" cannot be found' %
                (cls.__name__, args, kwargs))
        return entity

BaseMixin = IdMixin(db.Integer)


# Language codes
class Language(HouraiTeahouseModel, BaseMixin):
    __tablename__ = "languages"

    _language_code = db.Column('language_code', db.String(10), nullable=False)
    _language_name = db.Column('language_name', db.String(50))

    def __init__(self, code, name):
        self._language_code = code
        self._language_name = name

    @property
    def code(self):
        return self.language_code

    @property
    def name(self):
        return self.language_name


# Sec 1: User AuthN & AuthZ

# User authN & metadata
class User(HouraiTeahouseModel, BaseMixin):
    __tablename__ = "user"

    _username = db.Column('username', db.String(64), nullable=False,
                          unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    permissions_id = db.Column(db.Integer, db.ForeignKey(
        'permissions.permissions_id'), nullable=False)
    permissions = db.relationship(
        'UserPermissions', backref=db.backref(
            'user', lazy='dynamic'))
    # TODO: user registration confirmation

    def __init__(self, email, username, password, permissions):
        self.email = email
        self.username = username
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')
        self.permissions = permissions
        self.registered_on = datetime.utcnow()

    def change_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(
            self.password.encode('utf-8'), password)

    @property
    def is_active(self):
        return True

    @property
    def permissions(self):
        return self.permissions

    @property
    def username(self):
        return self._username

    def __repr__(self):
        return '<User {0}>'.format(self.username)

# Session tracking


class UserSession(HouraiTeahouseModel, BaseMixin):
    __tablename__ = "sessions"

    _session_uuid = db.Column('session_uuid', db.String(36), nullable=False,
                              unique=True)
    _valid_after = db.Column('valid_after', db.DateTime, nullable=False)
    _valid_before = db.Column('valid_before', db.DateTime, nullable=True)
    _user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.user_id'),
        nullable=False)
    _user = db.relationship(
        'User', backref=db.backref(
            'session', lazy='dynamic'))

    def __init__(self, user, remember_me=False):
        self.user = user
        self.session_uuid = str(uuid.uuid4())
        self.valid_after = datetime.utcnow()  # Prevent time travel
        if remember_me:
            self.valid_before = None
        else:
            self.valid_before = datetime.utcnow() + timedelta(days=1)

    @property
    def expiration(self):
        return None if self.valid_before is None else int(
            time.mktime(self.valid_before.timetuple())) * 1000

    @property
    def is_valid(self):
        now = datetime.utcnow()
        if self.valid_before is not None and self.valid_before < now:
            return False
        return self.valid_after < now

    @property
    def user(self):
        return self._user

    @property
    def uuid(self):
        return self._session_uuid

    def __repr__(self):
        return '<UserSession {0}>'.format(self._session_uuid)

# User authZ


class UserPermissions(HouraiTeahouseModel, BaseMixin):
    __tablename__ = "permissions"

    # Someone with host & DB access. admins cannot change a master's
    # permissions. This can only be set manually.  Equivalent of "webmaster"
    master = db.Column(db.Boolean, nullable=False, default=False)
    # User administrative rights - can edit people's permissions.  Only
    # masters can set this.  Essential moderator powers/etc.
    admin = db.Column(db.Boolean, nullable=False, default=False)
    # User is a member of our team.  They have access to our internal tools,
    # but not necessarily every action.
    team = db.Column(db.Boolean, nullable=False, default=False)
    # Permission to edit Wiki pages
    wiki = db.Column(db.Boolean, nullable=False, default=False)
    # Permission to post news (specifical new posts
    news = db.Column(db.Boolean, nullable=False, default=False)
    # Permission to translate existing content.  Does not allow new posting,
    # etc
    translate = db.Column(db.Boolean, nullable=False, default=False)
    # Permission to comment on news.  Can be revoked.
    comment = db.Column(db.Boolean, nullable=False, default=True)

    def __init(
            self,
            admin=False,
            team=False,
            wiki=False,
            news=False,
            comment=True):
        self.admin = admin
        self.team = team
        self.wiki = wiki
        self.news = news
        self.comment = comment

    @property
    def is_super_user(self):
        return self.admin or self.master

    def check_permission(self, permission):
        return self.is_super_user or getattr(self, permission, False)

    def update_permissions(self, newPermissions):
        for permType, value in newPermissions.items():
            if getattr(self, permType) != value:
                if permType == 'master':
                    raise Exception('Master can only be set manually!')
                setattr(self, permType, value)


# Sec 2: News, tags, comments

# A news post.
class NewsPost(HouraiTeahouseModel, BaseMixin):
    __tablename__ = "news"

    post_short = db.Column(db.String(64), nullable=False, unique=True)
    title = db.Column(db.String(1000), nullable=False, unique=True)
    # If someone tries to post a media URL > 1024 chars I will end them
    media = db.Column(db.String(1024))
    author_id = db.Column(
        db.Integer,
        db.ForeignKey('user.user_id'),
        nullable=False)
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

    def get_short(self):
        return self.post_short

    def get_author(self):
        return self.author

    def __repr__(self):
        return '<NewsPost {0}>'.format(self.title)


# Localized news titles. Many-to-one.
class NewsTitle(HouraiTeahouseModel):
    __tablename__ = "newstitle"

    _id = db.Column(
        db.Integer,
        db.ForeignKey('news.post_id'),
        nullable=False,
        primary_key=True)
    news = db.relationship('NewsPost',
                           backref=db.backref('newstitle', lazy='dynamic'))
    language_id = db.Column(
        db.Integer,
        db.ForeignKey('languages.language_id'),
        nullable=False,
        primary_key=True)
    language = db.relationship('Language',
                               backref=db.backref('newstitle', lazy='dynamic'))
    localized_title = db.Column(db.String(1000))

    @property
    def id(self):
        return self._id

    def __init__(self, news, language, title):
        self.news = news
        self.language = language
        self.localized_title = title

    def get_title(self):
        return self.localized_title


# Tags for news. Many-to-many.
class NewsTag(HouraiTeahouseModel, BaseMixin):
    __tablename__ = "newstag"

    name = db.Column(db.String(64), nullable=False, unique=True)
    news = db.relationship('NewsPost', secondary=tags, back_populates="tags")

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<NewsTag {0}>'.format(self.name)


# Comments on a news post.  Many-to-one.
class NewsComment(HouraiTeahouseModel, BaseMixin):
    __tablename__ = "newscomment"

    # Don't ask about the exact #. It's a mysql bug.
    body = db.Column(db.String(10000), nullable=False)
    author_id = db.Column(
        db.Integer,
        db.ForeignKey('user.user_id'),
        nullable=False)
    _author = db.relationship('User', backref=db.backref('newscomment',
                                                         lazy='dynamic'))
    news_id = db.Column(
        db.Integer,
        db.ForeignKey('news.post_id'),
        nullable=False)
    news = db.relationship('NewsPost',
                           backref=db.backref('newscomment', lazy='dynamic'))

    def __init__(self, body, author, news):
        self.body = body
        self._author = author
        self.news = news

    @property
    def author(self):
        return self._author
