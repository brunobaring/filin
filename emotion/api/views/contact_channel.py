from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView
from emotion.models import ContactChannel, SCOPE_GET_CONTACT_CHANNELS
from emotion.api.helper.decorators import user_restricted
from emotion.api.views.http_error import HTTPError
from emotion import db



contact_channel_blueprint = Blueprint('contact_channel', __name__)



class ContactChannelAPI(MethodView):

	@user_restricted([SCOPE_GET_CONTACT_CHANNELS])
	def get(self):
		contact_channels = []
		for contact_channel in db.session.query(ContactChannel).all():
			contact_channels.append(contact_channel.as_dict())

		responseObject = {
			'status': 'success',
			'data': {
				'contact_channels': contact_channels
			}
		}
		return make_response(jsonify(responseObject)), 200



contact_channel_view = ContactChannelAPI.as_view('contact_channel_api')



contact_channel_blueprint.add_url_rule('/contact_channel', view_func=contact_channel_view, methods=['GET'])
