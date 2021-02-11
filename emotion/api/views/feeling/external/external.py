from flask import Blueprint, request, make_response, jsonify, current_app, send_file
from flask.views import MethodView
from flask_bcrypt import Bcrypt
from emotion.models import Feeling, FeelingFile, SCOPE_GET_FEELING_BY_EXTERNAL_UUID
from emotion.api.helper.decorators import token_required
from emotion.api.helper.helpers import save_file, is_valid_uuid, has_permission
from emotion import db
import os, pathlib, io, zipfile



external_blueprint = Blueprint('external', __name__)



class ExternalAPI(MethodView):

	def post(self):
		if has_permission(request, SCOPE_GET_FEELING_BY_EXTERNAL_UUID) is None:
			responseObject = {
				'status': 'fail',
				'message': 'No permission'
			}
			return make_response(jsonify(responseObject)), 401

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
		if has_permission(request, SCOPE_GET_FEELING_BY_EXTERNAL_UUID) is None:
			responseObject = {
				'status': 'fail',
				'message': 'No permission'
			}
			return make_response(jsonify(responseObject)), 401

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

		feeling_files = FeelingFile.query.filter_by(feeling_id=feeling.internal_uuid).all()
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



external_view = ExternalAPI.as_view('external_api')



external_blueprint.add_url_rule('/external', view_func=external_view, methods=['GET', 'POST'])