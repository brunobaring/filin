from flask import request, make_response, jsonify, current_app
from emotion.models import User, Scope, RoleScope
from werkzeug.exceptions import RequestEntityTooLarge
from emotion.api.helper.helpers import check_apikey
from emotion.models import ROLE_COMPANY
from emotion.api.views.http_error import HTTPError
from functools import wraps
import math
import os



def user_restricted(scopes):
	def decorator(func):
		@wraps(func)
		def wrapper(*args, **kwargs):
			auth_header = request.headers.get('Authorization')
			if auth_header is None:
				return HTTPError(401, 'Missing Authorization header').to_dict()

			auth_header = auth_header.split(" ")
			if len(auth_header) <= 1 or auth_header[0] != 'Token' or auth_header[1] is None:
				return HTTPError(401, 'Token header malformed').to_dict()

			auth_token = auth_header[1]
			user_id = User.decode_auth_token(auth_token)
			user = User.query.filter_by(id_=user_id).first()
			if not user:
				return HTTPError(401, 'User not found').to_dict()

			if user.role.name == ROLE_COMPANY:
				check_apikey_result = check_apikey(request, user)
				if isinstance(check_apikey_result, HTTPError):
					return check_apikey_result

			for scope in scopes:
				restricted_scope = Scope.query.filter_by(name=scope).first()
				role_scope = RoleScope.query.filter_by(scope=restricted_scope).filter_by(role=user.role).first()
				if role_scope is None:
					print(scope)
					return HTTPError(403, 'Access denied.').to_dict()

			print(user_id, scopes)
			return func(*args, **kwargs)
		return wrapper
	return decorator



def check_file(view_method):
	@wraps(view_method)
	def decorated(*args, **kwargs):
		if 'file' in request.files:
			param_name = 'file'
		elif 'file[]' in request.files:
			param_name = 'file[]'
		else:
			return HTTPError(400, 'Missing files.').to_dict()

		try:
			file = request.files[param_name]
		except RequestEntityTooLarge as e:
			return HTTPError(400, 'Upload should have ' + str(math.floor(current_app.config['MAX_CONTENT_LENGTH'] / 1000000)) + 'MB max.').to_dict()
		
		file_ext = os.path.splitext(file.filename)[1]
		if file_ext not in current_app.config['UPLOAD_EXTENSIONS']:
			return HTTPError(400, 'Support only *' + (', *').join(current_app.config['UPLOAD_EXTENSIONS'])).to_dict()

		return view_method(*args, **kwargs)

	return decorated
