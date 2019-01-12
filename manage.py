from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand
from info import models
from info import create_app,db
from flask import render_template

app=create_app('development')
manage=Manager(app)
Migrate(app,db)
manage.add_command('db',MigrateCommand)

if __name__ == '__main__':
    print(app.url_map)
    manage.run()