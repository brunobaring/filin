from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView
from emotion.models import User, SCOPE_GET_USER
from emotion.api.helper.decorators import user_restricted
from emotion.api.views.http_error import HTTPError
from emotion import db



user_blueprint = Blueprint('user', __name__)



class UserAPI(MethodView):

	@user_restricted([SCOPE_GET_USER])
	def get(self):
		auth_token = request.headers.get('Authorization').split(" ")[1]
		user_id = User.decode_auth_token(auth_token)
		user = User.query.filter_by(id_=user_id).first()
		
		responseObject = {
			'user': user.as_dict()
		}
		return HTTPError(200).to_dict(responseObject)



user_view = UserAPI.as_view('user_api')



user_blueprint.add_url_rule('/user', view_func=user_view, methods=['GET'])
