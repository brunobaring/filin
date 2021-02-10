from flask import Blueprint, request, make_response, jsonify, current_app
from flask.views import MethodView
from emotion import db
from emotion.models import User, Feeling, Receiver, FeelingFile
from werkzeug.exceptions import RequestEntityTooLarge
from functools import wraps
from emotion.api.helper.decorators import token_required, check_file
from emotion.api.helper.helpers import get_folder_size, save_file
import os
import math



feeling_blueprint = Blueprint('feeling', __name__)



class FeelingAPI(MethodView):

	decorators = [token_required]

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
			receiver = Receiver(contact_channel_id, contact_channel_description, address, zipcode)
			feeling = Feeling(user, receiver, company_id, order_id, password)

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

				save_file(feeling, file_from_request, feeling_file)

				feeling_file_dicts.append(feeling_file.as_dict())

			db.session.commit()

		elif feeling_uuid is not None and request.path.split('/')[-1] == 'file':

			file_from_request = request.files.get('file')
			filename = file_from_request.filename

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

			save_file(feeling, file_from_request, feeling_file)

			feeling_files = FeelingFile.query.filter_by(feeling_id=feeling_uuid).all()
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

	def delete(self, feeling_uuid, feeling_file_uuid):

		feeling = Feeling.query.filter_by(internal_uuid=feeling_uuid).first()
		feeling_file = FeelingFile.query.filter_by(uuid=feeling_file_uuid).first()

		if feeling is None:
			responseObject = {
				'status': 'fail',
				'message': 'Feeling not found.'
			}

			return make_response(jsonify(responseObject)), 400

		if feeling_file is None:
			responseObject = {
				'status': 'fail',
				'message': 'Feeling File not found.'
			}

			return make_response(jsonify(responseObject)), 400

		os.remove(current_app.config['UPLOAD_PATH'] + '/' + str(feeling.id_) + '/' + str(feeling_file.uuid))

		db.session.delete(feeling_file)
		db.session.commit()

		feeling_files = FeelingFile.query.filter_by(feeling_id=feeling_uuid).all()
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



feeling_view = FeelingAPI.as_view('feeling_api')



feeling_blueprint.add_url_rule('/feeling', view_func=feeling_view, methods=['POST'], defaults={'feeling_uuid': None})
feeling_blueprint.add_url_rule('/feeling/<string:feeling_uuid>/file', view_func=feeling_view, methods=['POST'])
feeling_blueprint.add_url_rule('/feeling/<string:feeling_uuid>/file/<string:feeling_file_uuid>', view_func=feeling_view, methods=['DELETE'])
feeling_blueprint.add_url_rule('/feeling', view_func=feeling_view, methods=['GET'])
