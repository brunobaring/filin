from flask import Blueprint, request, make_response, jsonify, current_app
from flask.views import MethodView
from emotion import db
from emotion.models import User, Feeling, FeelingFile, SCOPE_CREATE_FEELING_FILE, SCOPE_DELETE_FEELING_FILE
from werkzeug.exceptions import RequestEntityTooLarge
from emotion.api.helper.decorators import token_required, check_file
from emotion.api.helper.helpers import get_folder_size, save_file, has_permission
import os
import math



feeling_file_blueprint = Blueprint('feeling_file', __name__)



class FeelingFileAPI(MethodView):

	decorators = [token_required]

	@check_file
	def post(self, internal_uuid):
		user = has_permission(request, SCOPE_CREATE_FEELING_FILE)
		if user is None:
			responseObject = {
				'status': 'fail',
				'message': 'No permission'
			}
			return make_response(jsonify(responseObject)), 401


		file_from_request = request.files.get('file')
		filename = file_from_request.filename

		feeling = Feeling.query.filter_by(internal_uuid=internal_uuid).first()

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

		feeling_files = FeelingFile.query.filter_by(feeling_id=internal_uuid).all()
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



	def delete(self, internal_uuid, feeling_file_uuid):
		if has_permission(request, SCOPE_DELETE_FEELING_FILE) is None:
			responseObject = {
				'status': 'fail',
				'message': 'No permission'
			}
			return make_response(jsonify(responseObject)), 401

		feeling = Feeling.query.filter_by(internal_uuid=internal_uuid).first()
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

		feeling_files = FeelingFile.query.filter_by(feeling_id=internal_uuid).all()
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



feeling_file_view = FeelingFileAPI.as_view('feeling_file_api')



feeling_file_blueprint.add_url_rule('/feeling/<string:internal_uuid>/file', view_func=feeling_file_view, methods=['POST'])
feeling_file_blueprint.add_url_rule('/feeling/<string:internal_uuid>/file/<string:feeling_file_uuid>', view_func=feeling_file_view, methods=['DELETE'])
