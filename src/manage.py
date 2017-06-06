from flask import url_for
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from houraiteahouse.config import DevelopmentConfig
from houraiteahouse.app import create_app
from houraiteahouse.storage.models import db

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
def routes():
    import urllib
    output = []
    for rule in app.url_map.iter_rules():
        options = {arg: '{%s}' % arg for arg in rule.arguments}
        methods = ','.join(rule.methods)
        url = url_for(rule.endpoint, **options)
        line = urllib.unquote(
            '{:50s} {:20s} {}'.format(rule.endpoint, methods, url))
        output.append(line)

    for line in sorted(output):
        print(line)


@manager.command
def create_admin():
  # Temporary for initialization - as part of this, connect to the DB &
  # create a real admin
  db.session.add(User(email='ad@min', password='admin', admin=True))
  db.session.commit()


@manager.command
def create_data():
  pass


if __name__ == '__main__':
  manager.run()
