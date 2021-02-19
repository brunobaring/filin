from flask import Blueprint, request, make_response, jsonify, current_app, send_file
from flask.views import MethodView
from flask_bcrypt import Bcrypt
from emotion.models import Feeling, FeelingFile, SCOPE_GET_FEELING_BY_EXTERNAL_UUID
from emotion.api.helper.decorators import user_restricted
from emotion.api.helper.helpers import save_file, is_valid_uuid
from emotion.api.views.http_error import HTTPError
from emotion import db
import os, pathlib, io, zipfile



external_blueprint = Blueprint('external', __name__)



class ExternalAPI(MethodView):

	@user_restricted([SCOPE_GET_FEELING_BY_EXTERNAL_UUID])
	def post(self):
		if 'external_uuid' not in request.form:
			return HTTPError(400, 'Expected params ["external_uuid"]').to_dict()

		external_uuid = request.form.get('external_uuid')
		feeling = Feeling.query.filter_by(external_uuid=external_uuid).first()

		if feeling is None:
			return HTTPError(400, 'Feeling not found.').to_dict()

		if feeling.password is not None:
			if 'password' not in request.form:
				return HTTPError(400, 'Expected params ["password"]').to_dict()

			password = request.form.get('password')
			bcrypt = Bcrypt()
			if not bcrypt.check_password_hash(feeling.password, password):
				return HTTPError(401, 'Invalid credentials').to_dict()

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



	@user_restricted([SCOPE_GET_FEELING_BY_EXTERNAL_UUID])
	def get(self):
		if 'external_uuid' not in request.form:
			return HTTPError(400, 'Expected params ["external_uuid"]').to_dict()

		external_uuid = request.form.get('external_uuid')
		feeling = Feeling.query.filter_by(external_uuid=external_uuid).first()

		if feeling is None:
			return HTTPError(400, 'Feeling not found.').to_dict()

		if feeling.password is not None:
			if 'password' not in request.form:
				return HTTPError(400, 'Expected params ["password"]').to_dict()

			password = request.form.get('password')
			bcrypt = Bcrypt()
			if not bcrypt.check_password_hash(feeling.password, password):
				return HTTPError(401, 'Invalid credentials').to_dict()

		feeling_files = FeelingFile.query.filter_by(feeling_id=feeling.internal_uuid).all()
		feeling_file_dicts = []
		for file in feeling_files:
			feeling_file_dicts.append(file.as_dict())

		feeling_dict = feeling.as_dict()
		feeling_dict['files'] = feeling_file_dicts

		responseObject = {
			'feeling': feeling_dict
		}
		return HTTPError(200).to_dict(responseObject)



external_view = ExternalAPI.as_view('external_api')



external_blueprint.add_url_rule('/external', view_func=external_view, methods=['GET', 'POST'])