from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView
from emotion.models import Company, SCOPE_GET_COMPANY_BY_ID, SCOPE_GET_ALL_COMPANIES, SCOPE_CREATE_COMPANIES
from emotion.api.helper.decorators import user_restricted
from emotion.api.views.http_error import HTTPError
from emotion import db
from sqlalchemy import exc



company_blueprint = Blueprint('company', __name__)



class CompanyAPI(MethodView):

	def get(self, company_id):
		if company_id is None:
			return self.get_companies()
		else:
			return self.get_company_by_id(company_id)



	@user_restricted([SCOPE_GET_ALL_COMPANIES])
	def get_companies(self):
		companies = Company.query.all()

		companiesObject = []
		for company in companies:
			companiesObject.append(company.as_dict_for_admin())

		responseObject = {
			'companies': companiesObject
		}
		return HTTPError(200).to_dict(responseObject)



	@user_restricted([SCOPE_GET_COMPANY_BY_ID])
	def get_company_by_id(self, company_id):
		company = Company.query.filter_by(id_=company_id).first()

		responseObject = {
			'company': company.as_dict_for_admin()
		}
		return HTTPError(200).to_dict(responseObject)



	@user_restricted([SCOPE_CREATE_COMPANIES])
	def post(self):
		company_name = request.form.get('name')
		if company_name is None:
			return HTTPError(400, 'Expected params ["name"]').to_dict()

		company = Company(company_name)
		db.session.add(company)
		try:
			db.session.commit()
		except exc.SQLAlchemyError:
			return HTTPError(400, 'Error while adding to database').to_dict()


		responseObject = {
			'company': company.as_dict_for_admin()
		}
		return HTTPError(200).to_dict(responseObject)



company_view = CompanyAPI.as_view('company_api')



company_blueprint.add_url_rule('/company', view_func=company_view, methods=['GET'], defaults={'company_id': None})
company_blueprint.add_url_rule('/company', view_func=company_view, methods=['POST'])
company_blueprint.add_url_rule('/company/<int:company_id>', view_func=company_view, methods=['GET'])
