from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from houraiteahouse.config import DevelopmentConfig
from houraiteahouse.app import create_app
from houraiteahouse.storage.models import db, Language

# Flask migrate scripting for SQLAlchemy

app = create_app(DevelopmentConfig())
migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)


@manager.command
def create_db():
    db.create_all()


@manager.command
def drop_db():
    db.drop_all()


@manager.command
def create_admin():
    # Temporary for initialization - as part of this, connect to the DB &
    # create a real admin
    db.session.add(User(email='ad@min', password='admin', admin=True))
    db.session.commit()

def get_lang(code, name):
    lang = Language.query.filter_by(language_code=code).first()
    if lang is None:
        db.session.add(Language(code, name))

@manager.command
def create_data():
    get_lang('en', 'English')
    get_lang('es', 'Spanish')
    get_lang('fr', 'French')
    get_lang('de', 'German')
    get_lang('zh-hans', 'Chinese Simplified')
    get_lang('zh-hant', 'Chinese Traditional')
    db.session.commit()

if __name__ == '__main__':
    manager.run()
