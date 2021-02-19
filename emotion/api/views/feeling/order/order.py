from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView
from emotion import db
from emotion.models import User, Feeling, Receiver, FeelingFile, SCOPE_GET_FEELING_BY_ORDER_ID
from emotion.api.helper.decorators import user_restricted, check_file
from emotion.api.helper.helpers import save_file, is_valid_uuid
from emotion.api.views.http_error import HTTPError



feeling_order_blueprint = Blueprint('feeling_order', __name__)



class FeelingOrderAPI(MethodView):

	@user_restricted([SCOPE_GET_FEELING_BY_ORDER_ID])
	def get(self, order_id):
		if order_id is None:
			return HTTPError(400, 'Expected params ["order_id"]').to_dict()

		feeling = Feeling.query.filter_by(order_id=order_id).first()
		if feeling is  None:
			return HTTPError(400, 'Feeling not found.').to_dict()

		responseObject = {
			'feeling': feeling.as_dict_for_company()
		}
		return HTTPError(200).to_dict(responseObject)



feeling_order_view = FeelingOrderAPI.as_view('feeling_order_api')



feeling_order_blueprint.add_url_rule('/feeling/order/<string:order_id>', view_func=feeling_order_view, methods=['GET'])