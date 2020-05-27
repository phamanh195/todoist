import os
from flask_script import Shell, Manager
from flask_migrate import Migrate, MigrateCommand
from app import create_app, db
from app.models import User, Note


app = create_app(os.environ.get('FLASK_CONFIG', 'default'))
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, User=User, Note=Note)

manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

@manager.command
def initialize_db():
    db.create_all()

if __name__ == '__main__':
    manager.run()
