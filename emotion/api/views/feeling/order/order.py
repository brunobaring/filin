from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView
from emotion import db
from emotion.models import User, Feeling, Receiver, FeelingFile, SCOPE_GET_FEELING_BY_ORDER_ID
from emotion.api.helper.decorators import token_required, check_file
from emotion.api.helper.helpers import save_file, is_valid_uuid, has_permission



feeling_order_blueprint = Blueprint('feeling_order', __name__)



class FeelingOrderAPI(MethodView):

	decorators = [token_required]

	def get(self, order_id):
		if has_permission(request, SCOPE_GET_FEELING_BY_ORDER_ID) is None:
			responseObject = {
				'status': 'fail',
				'message': 'No permission'
			}
			return make_response(jsonify(responseObject)), 401

		if order_id is None:
			responseObject = {
				'status': 'fail',
				'message': 'Missing order_id'
			}
			return make_response(jsonify(responseObject)), 401

		feeling = Feeling.query.filter_by(order_id=order_id).first()
		if feeling is  None:
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



feeling_order_view = FeelingOrderAPI.as_view('feeling_order_api')



feeling_order_blueprint.add_url_rule('/feeling/order/<string:order_id>', view_func=feeling_order_view, methods=['GET'])