from flask import Blueprint, request, make_response, jsonify, current_app
from flask.views import MethodView
from emotion import db
from emotion.models import Company, ContactChannel



defaults_blueprint = Blueprint('defaults', __name__)



class DefaultsAPI(MethodView):

	def post(self):

		db.session.add(ContactChannel('whatsapp'))
		db.session.add(ContactChannel('email'))
		db.session.add(ContactChannel('telegram'))
		db.session.add(Company('Americanas'))
		db.session.add(Company('Magalu'))
		db.session.add(Company('Boticario'))
		db.session.add(Company('Amazon'))
		db.session.commit()

		responseObject = {
			'status': 'success',
			'message': 'Defaults created'
		}
		return make_response(jsonify(responseObject)), 201



defaults_view = DefaultsAPI.as_view('defaults_api')



defaults_blueprint.add_url_rule('/defaults', view_func=defaults_view, methods=['POST'])
