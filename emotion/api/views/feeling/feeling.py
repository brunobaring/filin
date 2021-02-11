from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView
from emotion import db
from emotion.models import User, Feeling, Receiver, FeelingFile, SCOPE_CREATE_FEELING
from emotion.api.helper.decorators import token_required, check_file
from emotion.api.helper.helpers import save_file, is_valid_uuid, has_permission



feeling_blueprint = Blueprint('feeling', __name__)



class FeelingAPI(MethodView):

	decorators = [token_required]

	def get(self):
		if 'order_id' not in request.args and 'internal_uuid' not in request.args:
			responseObject = {
				'status': 'fail',
				'message': 'Missing params order_id or internal_uuid'
			}
			return make_response(jsonify(responseObject)), 401

		order_id = request.args.get('order_id')
		internal_uuid = request.args.get('internal_uuid')


		if order_id is not None:
			feeling = Feeling.query.filter_by(order_id=order_id).first()
		if internal_uuid is not None:
			if is_valid_uuid(str(internal_uuid)):
				feeling = Feeling.query.filter_by(internal_uuid=internal_uuid).first()
			else:
				responseObject = {
					'status': 'fail',
					'message': 'Invalid UUID format.'
				}
				return make_response(jsonify(responseObject)), 401


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
	def post(self):
		# auth_header = request.headers.get('Authorization')
		# auth_token = auth_header.split(" ")[1]
		# resp = User.decode_auth_token(auth_token)
		# user = User.query.filter_by(id_=resp).first()

		user = has_permission(request, SCOPE_CREATE_FEELING)

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



feeling_blueprint.add_url_rule('/feeling', view_func=feeling_view, methods=['POST'])
feeling_blueprint.add_url_rule('/feeling', view_func=feeling_view, methods=['GET'])
