from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView
from flask_bcrypt import Bcrypt
from emotion.models import User, Role, ROLE_ADMIN
from emotion.api.helper.decorators import token_required
from emotion.api.views.http_error import HTTPError
from emotion import db



auth_blueprint = Blueprint('auth', __name__)



class AuthAPI(MethodView):

	def post(self):
		path = request.path.split('/')[-1]

		if path == 'register':
			return self.post_register()
		elif path == 'login':

			return self.post_login()
		else: 
			return HTTPError(404, 'Invalid url path.').to_dict()


	def post_register(self):
		post_data = request.get_json()

		user = User.query.filter_by(email=post_data.get('email')).first()
		role = Role.query.filter_by(name=ROLE_ADMIN).first()
		if role is None:
			return HTTPError(400, 'No role detected. Contact admin').to_dict()

		if user:
			return HTTPError(400, 'User already exists. Please Log in.').to_dict()

		email = post_data.get('email')
		name = post_data.get('name')
		password = post_data.get('password')

		print(email, name, password)
		if email is None or name is None or password is None:
			return HTTPError(400, 'Expected params ["email", "name", "password"]').to_dict()

		user = User(
			email=email,
			name=name,
			password=password,
			role=role
		)

		db.session.add(user)
		db.session.commit()

		auth_token = user.encode_auth_token(user.id_)
		responseObject = {
			'auth_token': auth_token.decode()
		}
		return HTTPError(200).to_dict(responseObject)


	def post_login(self):
		post_data = request.get_json()

		email = post_data.get('email')
		password = post_data.get('password')
		if email is None or password is None:
			return HTTPError(400, 'Expected params ["email", "password"]').to_dict()

		user = User.query.filter_by(email=email).first()
		bcrypt = Bcrypt()
		if user and bcrypt.check_password_hash(user.password, password):
			auth_token = user.encode_auth_token(user.id_)
			responseObject = {
				'auth_token': auth_token.decode()
			}
			return HTTPError(200).to_dict(responseObject)
		else:
			return HTTPError(401, 'Invalid credentials.').to_dict()



auth_view = AuthAPI.as_view('auth_api')



auth_blueprint.add_url_rule('/auth/register', view_func=auth_view, methods=['POST'])
auth_blueprint.add_url_rule('/auth/login', view_func=auth_view, methods=['POST'])
