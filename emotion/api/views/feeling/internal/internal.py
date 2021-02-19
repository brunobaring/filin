from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView
from emotion import db
from emotion.models import User, Feeling, Receiver, FeelingFile, SCOPE_GET_FEELING_BY_INTERNAL_UUID, SCOPE_CREATE_FEELING
from emotion.api.helper.decorators import user_restricted, check_file
from emotion.api.helper.helpers import save_file, is_valid_uuid
from emotion.api.views.http_error import HTTPError
from sqlalchemy import exc



feeling_internal_blueprint = Blueprint('feeling_internal', __name__)



class FeelingInternalAPI(MethodView):

	@user_restricted([SCOPE_GET_FEELING_BY_INTERNAL_UUID])
	def get(self, internal_uuid):
		if internal_uuid is None:
			return HTTPError(400, 'Missing /:internal_uuid').to_dict()

		if is_valid_uuid(str(internal_uuid)):
			try:
				feeling = Feeling.query.filter_by(internal_uuid=internal_uuid).first()
			except exc.SQLAlchemyError:
				return HTTPError(400, 'Feeling not found').to_dict()
		else:
			return HTTPError(400, 'Invalid UUID format.').to_dict()

		if feeling is None:
			return HTTPError(400, 'Feeling not found').to_dict()

		responseObject = {
			'feeling': feeling.as_dict_for_company()
		}
		return HTTPError(200).to_dict(responseObject)



	@user_restricted([SCOPE_CREATE_FEELING])
	@check_file
	def post(self):
		auth_token = request.headers.get('Authorization').split(" ")[1]
		user_id = User.decode_auth_token(auth_token)
		user = User.query.filter_by(id_=user_id).first()

		files_list = request.files.getlist('file[]')

		if len(files_list) > 3:
			return HTTPError(400, 'More than 3 files received.').to_dict()

		contact_channel_id = request.form.get('contact_channel_id')
		contact_channel_description = request.form.get('contact_channel_description')
		address = request.form.get('address')
		zipcode = request.form.get('zipcode')
		company_id = request.form.get('company_id')
		order_id = request.form.get('order_id')
		password = request.form.get('password')
		if contact_channel_id is None or contact_channel_description is None or address is None or zipcode is None or company_id is None or order_id is None or password is None:
			return HTTPError(400, 'Expected params ["contact_channel_id", "contact_channel_description", "address", "zipcode", "company_id", "order_id", "password"]').to_dict()

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

		feeling_dict = feeling.as_dict()
		feeling_dict['files'] = feeling_file_dicts

		responseObject = {
			'feeling': feeling_dict
		}
		return HTTPError(200).to_dict(responseObject)



feeling_internal_view = FeelingInternalAPI.as_view('feeling_internal_api')



feeling_internal_blueprint.add_url_rule('/feeling/internal', view_func=feeling_internal_view, methods=['POST'])
feeling_internal_blueprint.add_url_rule('/feeling/internal/<string:internal_uuid>', view_func=feeling_internal_view, methods=['GET'])
