import json
import logging
import os
from datetime import datetime
from houraiteahouse.app import app, db
from houraiteahouse import models

logger = logging.getLogger(__name__)


# TODO: Major refactor to remove a lot of code duplication and cache read calls


def list_news(language='en'):
    news = models.NewsPost.query.order_by(models.NewsPost.created.desc()).all()
    if news is None or news == []:
        return None
    newsList = []
    for post in news:
        newsList.append(news_to_dict(post, None, language))
    return newsList


def tagged_news(tag):
    tag = models.NewsTag.query.filter_by(name=tag).first()
    if tag is None or tag.news is None:
        return None
    newsList = []
    for post in tag.news:
        newsList.append(news_to_dict(post, None))
    return newsList


# "postId" is a misnomer, it's actually the short title (ie, [date]-shortened-title)
def get_news(postId, session_id, language='en'):
    news = models.NewsPost.query.filter_by(post_short=postId).first()
    if news is None:
        return None

    caller = None
    if session_id is not None:
        caller = models.UserSession.query.filter_by(
            session_uuid=session_id).first().get_user()

    ret = news_to_dict(news, caller, language)

    with open('/var/htwebsite/news/' + language + '/' + postId, 'r') as file:
        ret['body'] = file.read()

    return ret


def post_news(title, body, tags, session_id, media=None, language='en'):
    tagObjs = []
    for tagName in tags:
        tag = get_tag(tagName)
        if tag is None:
            return None
        tagObjs.append(tag)

    author = models.UserSession.query.filter_by(
        session_uuid=session_id).first().get_user()
    if author is None:
        return None

    body = body.replace('\n', '<br />')  # replace linebreaks with HTML breaks

    created = datetime.utcnow()
    shortTitle = readDate(created) + '-' + title.replace(' ', '-')[:53]
    file = open('/var/htwebsite/news/' + language + '/' + shortTitle, 'w')
    file.write(body)
    file.close()

    news = models.NewsPost(shortTitle, title, created, author, tagObjs, media)
    try:
        db.session.add(news)
        db.session.commit()
        success = True
    except Exception as e:
        logger.exception('Failed to create news post: {0}'.format(e))
        success = False
    db.session.close()
    return get_news(shortTitle, session_id, language) if success else None


def edit_news(post_id, title, body, session_id, media, language='en'):
    news = models.NewsPost.query.filter_by(post_short=post_id).first()
    if news is None:
        return None

    caller = models.UserSession.query.filter_by(
        session_uuid=session_id).first().get_user()
    if caller != news.get_author():
        raise PermissionError

    body = body.replace('\n', '<br />')  # replace linebreaks with HTML breaks

    file = open('/var/htwebsite/news/' + language + '/' + news.post_short, 'w')
    file.write(body)
    file.close()

    news.title = title
    news.media = media
    news.lastEdit = datetime.utcnow()

    ret = news_to_dict(news, caller)

    try:
        db.session.merge(news)
        db.session.commit()
        db.session.close()
        ret['body'] = body
        return ret
    except Exception as e:
        logger.exception('Failed to edit comment: {0}'.format(e))
        db.session.close()
        raise e


def translate_news(post_id, language, title, body):
    news = models.NewsPost.query.filter_by(post_short=post_id).first()
    if news is None:
        return None
    lang = models.Language.query.filter_by(language_code=language).first()
    if(lang is None):
        return None

    body = body.replace('\n', '<br />')  # replace linebreaks with HTML breaks

    file = open('/var/htwebsite/news/' + language + '/' + news.post_short, 'w')
    file.write(body)
    file.close()

    ret = False
    title = models.NewsTitle.query.filter_by(news=news, language=lang).first()
    if(title is None):
        title = models.NewsTitle(news, lang, title)
        ret = True

    try:
        db.session.add(title)
        db.session.commit()
        db.session.close()
        return ret
    except Exception as e:
        logger.exception('Failed to post translation: {0}'.format(e))
        db.session.close()
        raise e


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
        logger.exception('Failed to create tag: {0}'.format(e))
        db.session.close()
        return -1


def post_comment(post_id, body, session_id):
    news = models.NewsPost.query.filter_by(post_short=post_id).first()
    if news is None:
        return None

    author = models.UserSession.query.filter_by(
        session_uuid=session_id).first().get_user()
    if author is None:
        return None
    ret = {'body': body, 'author': author.username}

    body = body.replace('\n', '<br />')  # replace linebreaks with HTML breaks

    comment = models.NewsComment(body, author, news)
    try:
        db.session.add(comment)
        db.session.commit()
        db.session.close()
        return ret
    except Exception as e:
        logger.exception('Failed to create comment: {0}'.format(e))
        db.session.close()
        raise e


def edit_comment(comment_id, body, session_id):
    comment = models.NewsComment.query.filter_by(comment_id=comment_id).first()
    if comment is None:
        return None

    caller = models.UserSession.query.filter_by(
        session_uuid=session_id).first().get_user()
    if caller != comment.get_author():
        raise PermissionError

    body = body.replace('\n', '<br />')

    comment.body = body

    try:
        db.session.merge(comment)
        db.session.commit()
        db.session.close()
    except Exception as e:
        logger.exception('Failed to edit comment: {0}'.format(e))
        db.session.close()
        raise e


def delete_comment(comment_id, session_id):
    comment = models.NewsComment.query.filter_by(comment_id=comment_id).first()
    if comment is None:
        return False

    caller = models.UserSession.query.filter_by(
        session_uuid=session_id).first().get_user()
    if caller != comment.get_author and not (
            caller.get_permissions().admin or caller.get_permissions().master):
        raise PermissionError

    try:
        db.session.delete(comment)
        db.session.commit()
        db.session.close()
    except Exception as e:
        logger.exception('Failed to delete comment: {0}'.format(e))
        db.session.close()
        raise e


def news_to_dict(news, caller, language='en'):
    try:
        lang = models.Language.query.filter_by(language_code=language).first()
    except Exception:
        logger.warning("Unrecognized language code {}".format(language))
        lang = models.Language.query.filter_by(language_code='en').first()

    newsDict = dict()
    newsDict['author'] = news.author.username
    newsDict['isAuthor'] = caller is not None and caller == news.get_author()
    newsDict['created'] = str(news.created)
    newsDict['post_id'] = news.post_short
    newsDict['tags'] = []

    title = models.NewsTitle.query.filter_by(
        news_id=news.get_id(), language_id=lang.get_id()).first()
    newsDict['title'] = title.get_title()

    if news.media is not None:
        newsDict['media'] = news.media

    for tag in news.tags:
        newsDict['tags'].append(tag.name)

    if news.comments:
        newsDict['comments'] = []
        for comment in news.comments:
            newsDict['comments'].append({'id': comment.comment_id, 'author': comment.get_author().get_username(
            ), 'body': comment.body, 'isAuthor': caller is not None and caller == comment.get_author()})

    if news.lastEdit:
        newsDict['lastEdit'] = str(news.lastEdit)

    return newsDict


def readDate(d):
    day = '0' + str(d.day) if d.day < 10 else d.day
    month = '0' + str(d.month) if d.month < 10 else d.month
    return '{0}-{1}-{2}'.format(d.year, month, day)
