from flask import Blueprint, request, make_response, jsonify, current_app
from flask.views import MethodView

from flask_bcrypt import Bcrypt
from emotion import db

from emotion.models import User, BlacklistToken, ContactChannel, Feeling, Receiver, FeelingFile, Company
import os, io, time 
import array
from werkzeug.exceptions import RequestEntityTooLarge
import json
from functools import wraps

import zipfile
from flask import send_file
import pathlib
import math

auth_blueprint = Blueprint('auth', __name__)


def get_folder_size(feeling_uuid):
	total_size = 0
	start_path = current_app.config['UPLOAD_PATH'] + "/" + str(feeling_uuid)
	for dirpath, dirnames, filenames in os.walk(start_path):
		print(dirpath)
		for f in filenames:
			fp = os.path.join(dirpath, f)
			# skip if it is symbolic link
			if not os.path.islink(fp):
				total_size += os.path.getsize(fp)

	return total_size


def token_required(view_method):
	@wraps(view_method)
	def decorated(*args, **kwargs):
		auth_header = request.headers.get('Authorization')
		if auth_header:
			try:
				auth_token = auth_header.split(" ")[1]
			except IndexError:
				responseObject = {
					'status': 'fail',
					'message': 'Bearer token malformed.'
				}
				return make_response(jsonify(responseObject)), 401
			if auth_header.split(" ")[0] != "Token":
				responseObject = {
					'status': 'fail',
					'message': 'Bearer token malformed.'
				}
				return make_response(jsonify(responseObject)), 401					
		else:
			responseObject = {
				'status': 'fail',
				'message': 'Provide a valid auth token.'
			}
			return make_response(jsonify(responseObject)), 401

		resp = User.decode_auth_token(auth_token)

		if isinstance(resp, str):
			responseObject = {
				'status': 'fail',
				'message': resp
			}
			return make_response(jsonify(responseObject)), 401			

		user = User.query.filter_by(id_=resp).first()
		if not user:
			responseObject = {
				'status': 'fail',
				'message': 'User not found.'
			}
			return make_response(jsonify(responseObject)), 401

		return view_method(*args, **kwargs)

	return decorated



class CompanyAPI(MethodView):

	def get(self, company_id):
		if company_id is None:
			companies = Company.query.all()

			companiesObject = []
			for company in companies:
				companiesObject.append(company.as_dict())

			responseObject = {
				'status': 'success',
				'data': {
					'companies': companiesObject
				}
			}

			return make_response(jsonify(responseObject)), 200

		else:
			company = Company.query.filter_by(id_=company_id).first()
			print(company)
			responseObject = {
				'status': 'success',
				'data': {
					'company': company.as_dict()
				}
			}

			return make_response(jsonify(responseObject)), 200


class DefaultsAPI(MethodView):

	def post(self):

		db.session.add(ContactChannel('whatsapp'))
		db.session.add(ContactChannel('email'))
		db.session.add(ContactChannel('telegram'))
		db.session.add(Company('Americanas'))
		db.session.add(Company('Magalu'))
		db.session.add(Company('Boticario'))
		db.session.add(Company('Amazon'))
		db.session.commit()

		responseObject = {
			'status': 'success',
			'message': 'Defaults created'
		}
		return make_response(jsonify(responseObject)), 201



class RegisterAPI(MethodView):
	"""
	User Registration Resource
	"""

	def post(self):
		# get the post data
		post_data = request.get_json()
		# check if user already exists


		user = User.query.filter_by(email=post_data.get('email')).first()
		if not user:
			try:
				user = User(
					email=post_data.get('email'),
					name=post_data.get('name'),
					password=post_data.get('password')
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



class LoginAPI(MethodView):
	"""
	User Login Resource
	"""

	def post(self):
		# get the post data
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


class UserAPI(MethodView):
	"""
	User Resource
	"""

	decorators = [token_required]

	def get(self):

		auth_header = request.headers.get('Authorization')
		auth_token = auth_header.split(" ")[1]

		resp = User.decode_auth_token(auth_token)
		user = User.query.filter_by(id_=resp).first()

		responseObject = {
			'status': 'success',
			'data': {
				'user_id': user.id_,
				'email': user.email,
				'name': user.name,
				'admin': user.admin,
				'created_at': user.created_at
			}
		}
		return make_response(jsonify(responseObject)), 200


class LogoutAPI(MethodView):
	"""
	Logout Resource
	"""

	decorators = [token_required]

	def post(self):
		# get auth token
		auth_header = request.headers.get('Authorization')
		auth_token = auth_header.split(" ")[1]

		blacklist_token = BlacklistToken(token=auth_token)
		try:
			# insert the token
			db.session.add(blacklist_token)
			db.session.commit()
			responseObject = {
				'status': 'success',
				'message': 'Successfully logged out.'
			}
			return make_response(jsonify(responseObject)), 200
		except Exception as e:
			responseObject = {
				'status': 'fail',
				'message': e
			}
			return make_response(jsonify(responseObject)), 200



class ExternalAPI(MethodView):

	def post(self):

		if 'external_uuid' not in request.form:
			responseObject = {
				'status': 'fail',
				'message': 'Missing params.'
			}
			return make_response(jsonify(responseObject)), 400

		external_uuid = request.form.get('external_uuid')
		feeling = Feeling.query.filter_by(external_uuid=external_uuid).first()

		if feeling is None:
			responseObject = {
				'status': 'fail',
				'message': 'Feeling not found.'
			}
			return make_response(jsonify(responseObject)), 404

		if feeling.password is not None:
			if 'password' not in request.form:
				responseObject = {
					'status': 'fail',
					'message': 'Missing params.'
				}
				return make_response(jsonify(responseObject)), 404

			password = request.form.get('password')
			bcrypt = Bcrypt()
			if not bcrypt.check_password_hash(feeling.password, password):
				responseObject = {
					'status': 'fail',
					'message': 'Wrong password.'
				}
				return make_response(jsonify(responseObject)), 404

		folder = os.path.abspath(current_app.config['UPLOAD_PATH'] + "/" + str(feeling.id_))
		base_path = pathlib.Path(folder)
		data = io.BytesIO()
		with zipfile.ZipFile(data, mode='w') as z:
			for f_name in base_path.iterdir():
				print(f_name)
				feeling_file = FeelingFile.query.filter_by(uuid=os.path.basename(f_name)).first()
				if feeling_file is None:
					continue
				z.write(f_name, "emotion/" + feeling_file.name, zipfile.ZIP_DEFLATED)
		data.seek(0)
		return send_file(
			data,
			mimetype='application/zip',
			as_attachment=True,
			attachment_filename='emotion.zip'
		)


	def get(self):

		if 'external_uuid' not in request.form:
			responseObject = {
				'status': 'fail',
				'message': 'Missing params.'
			}
			return make_response(jsonify(responseObject)), 400

		external_uuid = request.form.get('external_uuid')
		feeling = Feeling.query.filter_by(external_uuid=external_uuid).first()

		if feeling is None:
			responseObject = {
				'status': 'fail',
				'message': 'Feeling not found.'
			}
			return make_response(jsonify(responseObject)), 404


		if feeling.password is not None:
			if 'password' not in request.form:
				responseObject = {
					'status': 'fail',
					'message': 'Missing params.'
				}
				return make_response(jsonify(responseObject)), 404

			password = request.form.get('password')
			bcrypt = Bcrypt()
			if not bcrypt.check_password_hash(feeling.password, password):
				responseObject = {
					'status': 'fail',
					'message': 'Wrong password.'
				}
				return make_response(jsonify(responseObject)), 404

		feeling_files = FeelingFile.query.filter_by(uuid=feeling.internal_uuid).all()
		feeling_file_dicts = []
		for file in feeling_files:
			feeling_file_dicts.append(file.as_dict())

		feeling_dict = feeling.as_dict()
		feeling_dict['files'] = feeling_file_dicts

		responseObject = {
			'status': 'success',
			'data': {
				'feeling': feeling_dict
			}
		}

		return make_response(jsonify(responseObject)), 200


class FeelingAPI(MethodView):
	"""
	User Resource
	"""

	def check_file(view_method):
		@wraps(view_method)
		def decorated(*args, **kwargs):

			if 'file' in request.files:
				param_name = 'file'
			elif 'file[]' in request.files:
				param_name = 'file[]'
			else:
				responseObject = {
					'status': 'fail',
					'message': 'Missing files.'
				}
				return make_response(jsonify(responseObject)), 400			

			try:
				file = request.files[param_name]
			except RequestEntityTooLarge as e:
				responseObject = {
					'status': 'fail',
					'message': 'Upload should have ' + str(math.floor(current_app.config['MAX_CONTENT_LENGTH'] / 1000000)) + 'MB max.'
				}
				return make_response(jsonify(responseObject)), 401
			
			file_ext = os.path.splitext(file.filename)[1]
			if file_ext not in current_app.config['UPLOAD_EXTENSIONS']:
				responseObject = {
					'status': 'fail',
					'message': 'Support only *' + (', *').join(current_app.config['UPLOAD_EXTENSIONS'])
				}
				return make_response(jsonify(responseObject)), 400			

			return view_method(*args, **kwargs)

		return decorated

	decorators = [token_required]

	def save_file(self, feeling, file, feeling_file):
		folder = os.path.join(current_app.config['UPLOAD_PATH'], str(feeling.id_))

		try:
			os.mkdir(folder)
		except OSError:
			print ("Creation of the directory %s failed" % folder)
		else:
			print ("Successfully created the directory %s " % folder)

		file.save(os.path.join(folder, str(feeling_file.uuid)))


	def get(self):
		if 'order_id' not in request.args:
			responseObject = {
				'status': 'fail',
				'message': 'Missing order_id'
			}
			return make_response(jsonify(responseObject)), 401

		try:
			order_id = request.args.get('order_id')
		except RequestEntityTooLarge as e:
			responseObject = {
				'status': 'fail',
				'message': 'Missing order_id'
			}
			return make_response(jsonify(responseObject)), 401

		feeling = Feeling.query.filter_by(order_id=order_id).first()

		if feeling is None:

			responseObject = {
				'status': 'fail',
				'message': 'Feeling not found.'
			}

			return make_response(jsonify(responseObject)), 200

		responseObject = {
			'status': 'success',
			'data': {
				'feeling': feeling.as_dict_for_company()
			}
		}

		return make_response(jsonify(responseObject)), 200



	@check_file
	def post(self, feeling_uuid):
		auth_header = request.headers.get('Authorization')
		auth_token = auth_header.split(" ")[1]

		resp = User.decode_auth_token(auth_token)
		user = User.query.filter_by(id_=resp).first()

		if feeling_uuid is None:

			files_list = request.files.getlist('file[]')

			if len(files_list) > 3:
				responseObject = {
					'status': 'fail',
					'message': 'More than 3 files received.'
				}
				return make_response(jsonify(responseObject)), 400			

			contact_channel_id = request.form.get('contact_channel_id')
			contact_channel_description = request.form.get('contact_channel_description')
			address = request.form.get('address')
			zipcode = request.form.get('zipcode')
			company_id = request.form.get('company_id')
			order_id = request.form.get('order_id')
			password = request.form.get('password')
			print(password)
			receiver = Receiver(contact_channel_id, contact_channel_description, address, zipcode)
			feeling = Feeling(user, receiver, company_id, order_id, password)
			print(feeling.password)

			db.session.add(receiver)
			db.session.add(feeling)

			feeling_file_dicts = []
			for file_from_request in files_list:
				filename = file_from_request.filename
									
				feeling_file = FeelingFile(feeling, filename)
				db.session.add(feeling_file)
				db.session.flush()
				db.session.refresh(feeling_file)
				db.session.refresh(feeling)

				self.save_file(feeling, file_from_request, feeling_file)

				feeling_file_dicts.append(feeling_file.as_dict())

			db.session.commit()

		elif feeling_uuid is not None and request.path.split('/')[-1] == 'file':

			file_from_request = request.files.get('file')
			filename = file_from_request.filename
			# print("qwd", get_folder_size(feeling_uuid), "10485760", get_folder_size(feeling_uuid) < 10485760, request.headers.get('Content-Length'))

			feeling = Feeling.query.filter_by(internal_uuid=feeling_uuid).first()

			if get_folder_size(feeling.internal_uuid) + int(request.headers.get('Content-Length')) > current_app.config['MAX_CONTENT_LENGTH']:
				responseObject = {
					'status': 'fail',
					'message': 'Cannot exceed ' + str(math.floor(current_app.config['MAX_CONTENT_LENGTH'] / 1000000)) + 'MB in total.'
				}

				return make_response(jsonify(responseObject)), 400


			if feeling.creator_id != user.id_:
				responseObject = {
					'status': 'fail',
					'message': 'Not allowed to edit other feelings'
				}

				return make_response(jsonify(responseObject)), 400


			feeling_file = FeelingFile(feeling, filename)

			db.session.add(feeling_file)
			db.session.flush()
			db.session.refresh(feeling_file)

			self.save_file(feeling, file_from_request, feeling_file)

			feeling_files = FeelingFile.query.filter_by(uuid=feeling_uuid).all()
			feeling_file_dicts = []
			for file in feeling_files:
				feeling_file_dicts.append(file.as_dict())

			db.session.commit()

		feeling_dict = feeling.as_dict()
		feeling_dict['files'] = feeling_file_dicts

		responseObject = {
			'status': 'success',
			'data': {
				'feeling': feeling_dict
			}
		}

		return make_response(jsonify(responseObject)), 200



class ContactChannelAPI(MethodView):

	decorators = [token_required]

	def get(self):
		auth_header = request.headers.get('Authorization')
		if auth_header:
			try:
				auth_token = auth_header.split(" ")[1]
				print(auth_token)
			except IndexError:
				responseObject = {
					'status': 'fail',
					'message': 'Bearer token malformed.'
				}
				return make_response(jsonify(responseObject)), 401
		else:
			responseObject = {
				'status': 'fail',
				'message': 'Provide a valid auth token.'
			}
			return make_response(jsonify(responseObject)), 401

		arr = []
		for id_ in db.session.query(ContactChannel).all():
			arr.append(id_.as_dict())

		return make_response(jsonify(arr)), 200




# define the API resources
registration_view = RegisterAPI.as_view('register_api')
login_view = LoginAPI.as_view('login_api')
user_view = UserAPI.as_view('user_api')
logout_view = LogoutAPI.as_view('logout_api')
feeling_view = FeelingAPI.as_view('feeling_api')
external_view = ExternalAPI.as_view('external_api')
contact_channels_view = ContactChannelAPI.as_view('contact_channels_api')
company_view = CompanyAPI.as_view('company_api')
defaults_view = DefaultsAPI.as_view('defaults_api')

# add Rules for API Endpoints
auth_blueprint.add_url_rule('/auth/register', view_func=registration_view, methods=['POST'])
auth_blueprint.add_url_rule('/auth/login', view_func=login_view, methods=['POST'])
auth_blueprint.add_url_rule('/auth/status', view_func=user_view, methods=['GET'])
auth_blueprint.add_url_rule('/auth/logout', view_func=logout_view, methods=['POST'])
auth_blueprint.add_url_rule('/feeling', view_func=feeling_view, methods=['POST'], defaults={'feeling_uuid': None})
auth_blueprint.add_url_rule('/feeling/<string:feeling_uuid>/file', view_func=feeling_view, methods=['POST'])
auth_blueprint.add_url_rule('/feeling', view_func=feeling_view, methods=['GET'])
auth_blueprint.add_url_rule('/external', view_func=external_view, methods=['GEt', 'POST'])
auth_blueprint.add_url_rule('/contact_channels', view_func=contact_channels_view, methods=['GET'])
auth_blueprint.add_url_rule('/company', view_func=company_view, methods=['GET'], defaults={'company_id': None})
auth_blueprint.add_url_rule('/company/<int:company_id>', view_func=company_view, methods=['GET'])
auth_blueprint.add_url_rule('/defaults', view_func=defaults_view, methods=['POST'])

