from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView
from emotion.models import Company, SCOPE_GET_COMPANY_BY_ID, SCOPE_GET_ALL_COMPANIES
from emotion.api.helper.helpers import has_permission
from emotion.api.views.http_error import HTTPError



company_blueprint = Blueprint('company', __name__)



class CompanyAPI(MethodView):

	def get(self, company_id):
		if company_id is None:
			if has_permission(request, SCOPE_GET_ALL_COMPANIES) is None:
				return HTTPError(403, 'Access denied.').to_dict()

			companies = Company.query.all()

			companiesObject = []
			for company in companies:
				companiesObject.append(company.as_dict())

			responseObject = {
				'companies': companiesObject
			}
			return HTTPError(200).to_dict(responseObject)

		else:
			if has_permission(request, SCOPE_GET_COMPANY_BY_ID) is None:
				return HTTPError(403, 'Access denied.').to_dict()

			company = Company.query.filter_by(id_=company_id).first()

			responseObject = {
				'company': company.as_dict()
			}
			return HTTPError(200).to_dict(responseObject)



company_view = CompanyAPI.as_view('company_api')



company_blueprint.add_url_rule('/company', view_func=company_view, methods=['GET'], defaults={'company_id': None})
company_blueprint.add_url_rule('/company/<int:company_id>', view_func=company_view, methods=['GET'])
