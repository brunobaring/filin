from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView
from emotion.models import User, SCOPE_GET_USER
from emotion.api.helper.decorators import token_required
from emotion.api.helper.helpers import has_permission
from emotion.api.views.http_error import HTTPError
from emotion import db



user_blueprint = Blueprint('user', __name__)



class UserAPI(MethodView):

	decorators = [token_required]

	def get(self):
		user = has_permission(request, SCOPE_GET_USER)
		if user is None:
			return HTTPError(403, 'Access denied.').to_dict()

		responseObject = {
			'user_id': user.id_,
			'email': user.email,
			'name': user.name,
			'role': user.user_role.name.lower(),
			'created_at': user.created_at
		}
		return HTTPError(200).to_dict(responseObject)



user_view = UserAPI.as_view('user_api')



user_blueprint.add_url_rule('/user', view_func=user_view, methods=['GET'])
