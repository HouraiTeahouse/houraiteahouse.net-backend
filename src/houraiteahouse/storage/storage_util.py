import logging
from houraiteahouse.storage.models import db, cache


def try_action(action):
    db_action = getattr(db.session, action)

    def try_action(**kwargs):
        for name, value in kwargs.items():
            try:
                if name == 'logger':
                    continue
                db_action(value)
                db.session.commit()
            except Exception as error:
                logger = logging
                if 'logger' in kwargs:
                    logger = kwargs['logger']
                logger.exception('Failed to {} {}: {}'.format(action, name,
                                                              error))
                db.session.close()
                raise
    return try_action


try_add = try_action('add')
try_delete = try_action('delete')
try_merge = try_action('merge')
