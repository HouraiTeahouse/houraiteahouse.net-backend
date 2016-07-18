import json
import logging
import os

from houraiteahouse.app import app, db
from houraiteahouse import models

logger = logging.getLogger(__name__)


def list_news():
    news = models.NewsPost.query.order_by(models.NewsPost.created.desc()).all()
    if news is None or news == []:
        return None
    newsList = []
    for post in news:
        newsList.append(news_to_dict(post))
    return newsList


def tagged_news(tag):
    tag = models.NewsTag.query.filter_by(name=tag).first()
    if tag is None or tag.news is None:
        return None
    newsList = []
    for post in tag.news:
        newsList.append(news_to_dict(post))
    return newsList


def get_news(postId):
    news = models.NewsPost.query.filter_by(id=postId).first()
    if news is None:
        return None
    return news_to_dict(news)


def post_news(title, body, tags):
    author = models.User.query.filter_by(username='LordAlfredo').first()
    tagObjs = []
    for tagName in tags:
        tag = get_tag(tagName)
        if tag == None:
            return False
        tagObjs.append(tag)
    news = models.NewsPost(title, body, author, tagObjs)
    try:
        db.session.add(news)
        db.session.commit()
        success = True
    except Exception as e:
        logger.exception('Failed to create news post: {0}'.format(e.message))
        success = False
    db.session.close()
    return models.NewsPost.query.filter_by(title=title).first() if success else None


def get_tag(name):
    tag = models.NewsTag.query.filter_by(name=name).first()
    if tag is None:
        return create_tag(name)
    return tag


def create_tag(name):
    tag = models.NewsTag(name)
    try:
        db.session.add(tag)
        db.session.commit()
        db.session.close()
        return models.NewsTag.query.filter_by(name=name).first()
    except Exception as e:
        logger.exception('Failed to create tag: {0}'.format(e.message))
        db.session.close()
        return -1


def news_to_dict(news):
    newsDict = dict()
    newsDict['author'] = news.author.username
    newsDict['created'] = str(news.created)
    newsDict['title'] = news.title
    newsDict['body'] = news.body
    newsDict['id'] = news.id
    newsDict['tags'] = []
    for tag in news.tags:
        newsDict['tags'].append(tag.name)
    return newsDict
