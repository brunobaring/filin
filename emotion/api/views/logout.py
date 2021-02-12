from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView
from emotion.models import BlacklistToken
from emotion.api.helper.decorators import token_required
from emotion.api.views.http_error import HTTPError
from emotion import db



logout_blueprint = Blueprint('logout', __name__)



class LogoutAPI(MethodView):

	decorators = [token_required]

	def post(self):
		auth_header = request.headers.get('Authorization')
		auth_token = auth_header.split(" ")[1]

		blacklist_token = BlacklistToken(token=auth_token)
		db.session.add(blacklist_token)
		db.session.commit()
		return HTTPError(200).to_dict()



logout_view = LogoutAPI.as_view('logout_api')



logout_blueprint.add_url_rule('/logout', view_func=logout_view, methods=['POST'])
