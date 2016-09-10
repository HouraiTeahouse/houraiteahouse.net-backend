import json
import logging
import os

from houraiteahouse.app import app, db
from houraiteahouse import models
from email._header_value_parser import Comment

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
    news = models.NewsPost.query.filter_by(post_id=postId).first()
    if news is None:
        return None
    return news_to_dict(news)


def post_news(title, body, tags, session_id, media=None):
    tagObjs = []
    for tagName in tags:
        tag = get_tag(tagName)
        if tag == None:
            return None
        tagObjs.append(tag)

    author = models.UserSession.query.filter_by(session_uuid=session_id).first().get_user()
    if author is None:
        return None
    
    body = body.replace('\n', '<br />') # replace linebreaks with HTML breaks
    
    news = models.NewsPost(title, body, author, tagObjs, media)
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
    

def post_comment(postId, body, session_id):
    news = models.NewsPost.query.filter_by(post_id=postId).first()
    if news is None:
        return None
    
    author = models.UserSession.query.filter_by(session_uuid=session_id).first().get_user()
    if author is None:
        return None
    ret = {'body': body, 'author': author.username}
    
    body = body.replace('\n', '<br />') # replace linebreaks with HTML breaks

    comment = models.NewsComment(body, author, news)
    try:
        db.session.add(comment)
        db.session.commit()
        db.session.close()
        return ret
    except Exception as e:
        logger.exception('Failed to create comment: {0}'.format(e.message))
        db.session.close()
        raise e


def news_to_dict(news):
    newsDict = dict()
    newsDict['author'] = news.author.username
    newsDict['created'] = str(news.created)
    newsDict['title'] = news.title
    newsDict['body'] = news.body
    newsDict['post_id'] = news.post_id
    newsDict['tags'] = []
    if news.media is not None:
        newsDict['media'] = news.media

    for tag in news.tags:
        newsDict['tags'].append(tag.name)
        
    if news.comments:
        newsDict['comments'] = []
        for comment in news.comments:
            newsDict['comments'].append({'author':comment.get_author_name(),'body':comment.body})

    return newsDict
