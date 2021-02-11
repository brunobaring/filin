from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView
from emotion.models import User
from emotion.api.helper.decorators import token_required
from emotion import db



user_blueprint = Blueprint('user', __name__)



class UserAPI(MethodView):

	decorators = [token_required]

	def get(self):
		auth_header = request.headers.get('Authorization')
		auth_token = auth_header.split(" ")[1]

		resp = User.decode_auth_token(auth_token)
		user = User.query.filter_by(id_=resp).first()

		responseObject = {
			'status': 'success',
			'data': {
				'user_id': user.id_,
				'email': user.email,
				'name': user.name,
				'role': user.user_role.name.lower(),
				'created_at': user.created_at
			}
		}
		return make_response(jsonify(responseObject)), 200



user_view = UserAPI.as_view('user_api')



user_blueprint.add_url_rule('/user', view_func=user_view, methods=['GET'])
