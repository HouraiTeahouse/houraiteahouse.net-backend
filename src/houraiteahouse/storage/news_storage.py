import json
import logging
import os
from datetime import datetime
from flask_sqlalchemy_cache import FromCache
from houraiteahouse.storage import auth_storage as auth
from houraiteahouse.storage import storage_util as util
from houraiteahouse.storage import models
from houraiteahouse.storage.models import db, cache

logger = logging.getLogger(__name__)

DEFAULT_LANGUAGE = 'en_US'


def sanitize_body(body):
    return body.replace('\n', '<br />')  # replace linebreaks with HTML breaks


def get_language(language=DEFAULT_LANGUAGE):
    try:
        lang = models.Language.get(language_code=language)
    except Exception:
        logger.warning('Unrecognized language code {}'.format(language))
        lang = models.Language.get(language_code=DEFAULT_LANGUAGE)
    return lang


def list_news(language=DEFAULT_LANGUAGE):
    news = models.NewsPost.query.order_by(models.NewsPost.created.desc()) \
        .options(FromCache(cache)).all()
    if not news:
        return None
    return [news_to_dict(post, language=language) for post in news]


def open_news_file(postId, language=DEFAULT_LANGUAGE, filemode='r'):
    post_path = os.path.join('/var/htwebsite/news/', language, postId)
    return open(post_path, filemode)


def tagged_news(tag, language=DEFAULT_LANGUAGE):
    tag = models.NewsTag.get(name=tag)
    if not tag or not tag.news:
        return None
    return [news_to_dict(post, language=language) for post in news]


# "postId" is a misnomer, it's actually the short title
# (ie, [date]-shortened-title)
def get_news(postId, session_id, language=DEFAULT_LANGUAGE):
    news = models.NewsPost.get(post_short=postId)
    if not news:
        return None

    caller = None
    if session_id:
        caller = auth.get_user_session(session_id).user

    ret = news_to_dict(news, caller, language)

    # TODO(james7132): Make this configurable
    with open_news_file(postId, language=language) as news_file:
        ret['body'] = news_filej.read()

    return ret


def post_news(title, body, tags, session_id, media=None,
              language=DEFAULT_LANGUAGE):
    lang = get_language(language)

    tagObjs = list()
    for tagName in tags:
        tag = get_tag(tagName)
        if tag:
            tagObjs.append(tag)

    author = auth.get_user_session(session_id).user
    if not author:
        return None

    body = sanitize_body(body)

    created = datetime.utcnow()
    shortTitle = readDate(created) + '-' + title.replace(' ', '-')[:53]
    with open_news_file(shortTitle, language, filemode='w') as news_file:
        news_file.write(body)

    news = models.NewsPost(shortTitle, title, created, author, tagObjs, media)

    postTitle = models.NewsTitle(news, lang, title)

    util.try_add(news=news, logger=logger)
    return get_news(shortTitle, session_id, language)


def edit_news(post_id, title, body, session_id, media,
              language=DEFAULT_LANGUAGE):
    news = models.NewsPost.get_or_die(post_short=post_id)
    caller = auth.get_user_session(session_id).user
    if caller != news.author:
        raise PermissionError

    body = sanitize_body(body)

    with open_news_file(news.post_short, language, filemode='w') as news_file:
        news_file.write(body)

    news.title = title
    news.media = media
    news.lastEdit = datetime.utcnow()

    ret = news_to_dict(news, caller)

    util.try_merge(news=news, logger=logger)
    ret['body'] = body
    return ret


def translate_news(post_id, language, title, body):
    news = models.NewsPost.get_or_die(post_short=post_id)
    lang = get_language(language)
    if not lang:
        return None

    body = sanitize_body(body)

    with open_news_file(news.post_short, language, filemode='w') as news_file:
        news_file.write(body)

    ret = False
    title = models.NewsTitle.get(news=news, language=lang)
    if not title:
        title = models.NewsTitle(news, lang, title)
        ret = True

    util.try_add(title=title, logger=logger)
    return ret


def get_tag(name):
    tag = models.NewsTag.get(name=name)
    return tag or create_tag(name)


def create_tag(name):
    util.try_add(tag=models.NewsTag(name), logger=logger)
    # It won't be in the cache yet, so we must actually load it.
    return models.NewsTag.get(name=name)


def post_comment(post_id, body, session_id):
    news = models.NewsPost.get_or_die(post_short=post_id)
    author = auth.get_user_session(session_id).user
    if not author:
        return None
    ret = {'body': body, 'author': author.username}

    body = sanitize_body(body)

    comment = models.NewsComment(body, author, news)
    util.try_add(comment=comment, logger=logger)
    return ret


def edit_comment(comment_id, body, session_id):
    comment = models.NewsComment.get_or_die(id=comment_id)
    caller = auth.get_user_session(session_id).user
    if caller != comment.author:
        raise PermissionError

    comment.body = sanitize_body(body)
    util.try_merge(comment=comment, logger=logger)


def delete_comment(comment_id, session_id):
    comment = models.NewsComment.get_or_die(id=comment_id)
    caller = auth.get_user_session(session_id).user
    if caller != comment.get_author and not (
            caller.get_permissions().admin or caller.get_permissions().master):
        raise PermissionError

    util.try_delete(comment=comment, logger=logger)
    return True


def news_to_dict(news, caller=None, language=DEFAULT_LANGUAGE):
    newsDict = {
        'author': news.author.username,
        'isAuthor': caller and caller == news.get_author(),
        'created': str(news.created),
        'post_id': news.post_short,
        'tags': [tag.name for tag in news.tags]
    }

    title = models.NewsTitle.query.filter_by(
        news_id=news.id, language_id=lang.id).first()
    newsDict['title'] = title.get_title() or news.title

    if news.media:
        newsDict['media'] = news.media

    if news.comments:
        newsDict['comments'] = [comment_to_dict(comment, caller)
                                for comment in news.comments]

    if news.lastEdit:
        newsDict['lastEdit'] = str(news.lastEdit)

    return newsDict


def comment_to_dict(comment, caller=None):
    return {
        'id': comment.comment_id,
        'author': comment.get_author() .get_username(),
        'body': comment.body,
        'isAuthor': caller and caller == comment.get_author()
    }


def readDate(d):
    day = '0' + str(d.day) if d.day < 10 else d.day
    month = '0' + str(d.month) if d.month < 10 else d.month
    return '{0}-{1}-{2}'.format(d.year, month, day)
