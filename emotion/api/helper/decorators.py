from flask import request, make_response, jsonify, current_app
from emotion.models import User
from werkzeug.exceptions import RequestEntityTooLarge
from functools import wraps
import math
import os



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

		user_id = User.decode_auth_token(auth_token)

		if isinstance(user_id, str):
			responseObject = {
				'status': 'fail',
				'message': user_id
			}
			return make_response(jsonify(responseObject)), 401			

		user = User.query.filter_by(id_=user_id).first()
		if not user:
			responseObject = {
				'status': 'fail',
				'message': 'User not found.'
			}
			return make_response(jsonify(responseObject)), 401

		return view_method(*args, **kwargs)

	return decorated



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
