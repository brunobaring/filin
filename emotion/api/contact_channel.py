from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView
from emotion.models import ContactChannel
from emotion.api.helper.decorators import token_required
from emotion import db



contact_channel_blueprint = Blueprint('contact_channel', __name__)



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



contact_channel_view = ContactChannelAPI.as_view('contact_channel_api')



contact_channel_blueprint.add_url_rule('/contact_channel', view_func=contact_channel_view, methods=['GET'])
