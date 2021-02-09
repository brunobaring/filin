import os
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager 
from flask_cors import CORS
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from sqlalchemy import event

# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()
from emotion import models, config

def create_app():
	app = Flask(__name__)
	CORS(app)

	app.config.from_object(os.getenv('APP_SETTINGS'))
	app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024   # 10MB
	app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif']

	db.init_app(app)

	bcrypt = Bcrypt(app)

	migrate = Migrate(app, db)
	migrate.init_app(app, db)

	manager = Manager(app)
	manager.add_command('db', MigrateCommand)

	login_manager = LoginManager()
	login_manager.login_view = 'auth.login'
	login_manager.init_app(app)
	
	from .models import User
	@login_manager.user_loader
	def load_user(user_id):
		# since the user_id is just the primary key of our user table, use it in the query for the user
		return User.query.get(int(user_id))

	# blueprint for auth routes in our app
	from emotion.auth.views import auth_blueprint
	app.register_blueprint(auth_blueprint)

	# blueprint for non-auth parts of app
	from . main import main as main_blueprint
	app.register_blueprint(main_blueprint)




	return app