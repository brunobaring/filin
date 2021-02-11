from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView
from emotion.models import Company, SCOPE_GET_COMPANY_BY_ID, SCOPE_GET_ALL_COMPANIES
from emotion.api.helper.helpers import has_permission



company_blueprint = Blueprint('company', __name__)



class CompanyAPI(MethodView):

	def get(self, company_id):
		if company_id is None:
			if has_permission(request, SCOPE_GET_ALL_COMPANIES) is None:
				responseObject = {
					'status': 'fail',
					'message': 'No permission'
				}
				return make_response(jsonify(responseObject)), 401

			companies = Company.query.all()

			companiesObject = []
			for company in companies:
				companiesObject.append(company.as_dict())

			responseObject = {
				'status': 'success',
				'data': {
					'companies': companiesObject
				}
			}

			return make_response(jsonify(responseObject)), 200

		else:
			if has_permission(request, SCOPE_GET_COMPANY_BY_ID) is None:
				responseObject = {
					'status': 'fail',
					'message': 'No permission'
				}
				return make_response(jsonify(responseObject)), 401

			company = Company.query.filter_by(id_=company_id).first()

			responseObject = {
				'status': 'success',
				'data': {
					'company': company.as_dict()
				}
			}
			return make_response(jsonify(responseObject)), 200



company_view = CompanyAPI.as_view('company_api')



company_blueprint.add_url_rule('/company', view_func=company_view, methods=['GET'], defaults={'company_id': None})
company_blueprint.add_url_rule('/company/<int:company_id>', view_func=company_view, methods=['GET'])
