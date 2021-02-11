from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView
from flask_bcrypt import Bcrypt
from emotion.models import User, UserRole, USER_ROLE_USER
from emotion.api.helper.decorators import token_required
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
			responseObject = {
				'status': 'fail',
				'message': 'Invalid url path.'
			}
			return make_response(jsonify(responseObject)), 401


	def post_register(self):
		post_data = request.get_json()

		user = User.query.filter_by(email=post_data.get('email')).first()
		user_role = UserRole.query.filter_by(name=USER_ROLE_USER).first()
		if user_role is None:
			responseObject = {
				'status': 'fail',
				'message': 'Some error occurred. Please try again.'
			}
			return make_response(jsonify(responseObject)), 401
		if not user:
			try:
				user = User(
					email=post_data.get('email'),
					name=post_data.get('name'),
					password=post_data.get('password'),
					user_role=user_role
				)

				# insert the user
				db.session.add(user)
				db.session.commit()
				# generate the auth token
				auth_token = user.encode_auth_token(user.id_)
				responseObject = {
					'status': 'success',
					'message': 'Successfully registered.',
					'auth_token': auth_token.decode()
				}
				return make_response(jsonify(responseObject)), 201
			except Exception as e:
				responseObject = {
					'status': 'fail',
					'message': 'Some error occurred. Please try again.'
				}
				print(e)
				return make_response(jsonify(responseObject)), 401
		else:
			responseObject = {
				'status': 'fail',
				'message': 'User already exists. Please Log in.',
			}
			return make_response(jsonify(responseObject)), 202



	def post_login(self):
		post_data = request.get_json()
		try:
			# fetch the user data
			user = User.query.filter_by(
				email=post_data.get('email')
			).first()
			bcrypt = Bcrypt()
			if user and bcrypt.check_password_hash(
				user.password, post_data.get('password')
			):
				auth_token = user.encode_auth_token(user.id_)
				if auth_token:
					responseObject = {
						'status': 'success',
						'message': 'Successfully logged in.',
						'auth_token': auth_token.decode()
					}
					return make_response(jsonify(responseObject)), 200
			else:
				responseObject = {
					'status': 'fail',
					'message': 'User does not exist.'
				}
				return make_response(jsonify(responseObject)), 404
		except Exception as e:
			print(e)
			responseObject = {
				'status': 'fail',
				'message': 'Try again'
			}
			return make_response(jsonify(responseObject)), 500



auth_view = AuthAPI.as_view('auth_api')



auth_blueprint.add_url_rule('/auth/register', view_func=auth_view, methods=['POST'])
auth_blueprint.add_url_rule('/auth/login', view_func=auth_view, methods=['POST'])
