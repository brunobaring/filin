import os
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager 
from flask_cors import CORS
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from sqlalchemy import event



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
		return User.query.get(int(user_id))

	from emotion.api.views.feeling.internal.internal import feeling_internal_blueprint
	app.register_blueprint(feeling_internal_blueprint)

	from emotion.api.views.company import company_blueprint
	app.register_blueprint(company_blueprint)

	from emotion.api.views.contact_channel import contact_channel_blueprint
	app.register_blueprint(contact_channel_blueprint)

	from emotion.api.views.defaults import defaults_blueprint
	app.register_blueprint(defaults_blueprint)

	from emotion.api.views.user import user_blueprint
	app.register_blueprint(user_blueprint)

	from emotion.api.views.logout import logout_blueprint
	app.register_blueprint(logout_blueprint)

	from emotion.api.views.auth import auth_blueprint
	app.register_blueprint(auth_blueprint)

	from emotion.api.views.feeling.external.external import external_blueprint
	app.register_blueprint(external_blueprint)

	from emotion.api.views.feeling.file.file import feeling_file_blueprint
	app.register_blueprint(feeling_file_blueprint)

	from emotion.api.views.feeling.order.order import feeling_order_blueprint
	app.register_blueprint(feeling_order_blueprint)

	return app