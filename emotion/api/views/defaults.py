from flask import Blueprint, request, make_response, jsonify, current_app
from flask.views import MethodView
from emotion import db
from emotion.models import Scope, UserRole, UserRoleScope, Company, FeelingFile, Feeling, User, ContactChannel, Receiver, BlacklistToken, SCOPE_GET_FEELING_EXTERNAL_UUID, SCOPE_GET_ALL_COMPANIES, SCOPE_GET_COMPANY_BY_ID, SCOPE_GET_CONTACT_CHANNELS, SCOPE_CREATE_FEELING, SCOPE_DELETE_FEELING_FILE, SCOPE_CREATE_FEELING_FILE, SCOPE_GET_USER, USER_ROLE_ADMIN, USER_ROLE_USER, USER_ROLE_COMPANY



defaults_blueprint = Blueprint('defaults', __name__)



class DefaultsAPI(MethodView):

	def post(self):

		db.session.query(UserRoleScope).delete()
		db.session.query(Scope).delete()
		db.session.query(UserRole).delete()
		db.session.query(FeelingFile).delete()
		db.session.query(Feeling).delete()
		db.session.query(Company).delete()
		db.session.query(User).delete()
		db.session.query(Receiver).delete()
		db.session.query(ContactChannel).delete()
		db.session.query(BlacklistToken).delete()

		db.session.add(ContactChannel('whatsapp'))
		db.session.add(ContactChannel('email'))
		db.session.add(ContactChannel('telegram'))
		db.session.add(Company('Americanas'))
		db.session.add(Company('Magalu'))
		db.session.add(Company('Boticario'))
		db.session.add(Company('Amazon'))

		obj_SCOPE_GET_FEELING_EXTERNAL_UUID = Scope(SCOPE_GET_FEELING_EXTERNAL_UUID)
		obj_SCOPE_GET_ALL_COMPANIES = Scope(SCOPE_GET_ALL_COMPANIES)
		obj_SCOPE_GET_COMPANY_BY_ID = Scope(SCOPE_GET_COMPANY_BY_ID)
		obj_SCOPE_GET_CONTACT_CHANNELS = Scope(SCOPE_GET_CONTACT_CHANNELS)
		obj_SCOPE_CREATE_FEELING = Scope(SCOPE_CREATE_FEELING)
		obj_SCOPE_DELETE_FEELING_FILE = Scope(SCOPE_DELETE_FEELING_FILE)
		obj_SCOPE_CREATE_FEELING_FILE = Scope(SCOPE_CREATE_FEELING_FILE)
		obj_SCOPE_GET_USER = Scope(SCOPE_GET_USER)
		obj_USER_ROLE_ADMIN = UserRole(USER_ROLE_ADMIN)
		obj_USER_ROLE_USER = UserRole(USER_ROLE_USER)
		obj_USER_ROLE_COMPANY = UserRole(USER_ROLE_COMPANY)

		db.session.add(obj_SCOPE_GET_FEELING_EXTERNAL_UUID)
		db.session.add(obj_SCOPE_GET_ALL_COMPANIES)
		db.session.add(obj_SCOPE_GET_COMPANY_BY_ID)
		db.session.add(obj_SCOPE_GET_CONTACT_CHANNELS)
		db.session.add(obj_SCOPE_CREATE_FEELING)
		db.session.add(obj_SCOPE_DELETE_FEELING_FILE)
		db.session.add(obj_SCOPE_CREATE_FEELING_FILE)
		db.session.add(obj_SCOPE_GET_USER)
		db.session.add(obj_USER_ROLE_ADMIN)
		db.session.add(obj_USER_ROLE_USER)
		db.session.add(obj_USER_ROLE_COMPANY)

		db.session.flush()

		db.session.refresh(obj_SCOPE_GET_FEELING_EXTERNAL_UUID)
		db.session.refresh(obj_SCOPE_GET_ALL_COMPANIES)
		db.session.refresh(obj_SCOPE_GET_COMPANY_BY_ID)
		db.session.refresh(obj_SCOPE_GET_CONTACT_CHANNELS)
		db.session.refresh(obj_SCOPE_CREATE_FEELING)
		db.session.refresh(obj_SCOPE_DELETE_FEELING_FILE)
		db.session.refresh(obj_SCOPE_CREATE_FEELING_FILE)
		db.session.refresh(obj_SCOPE_GET_USER)
		db.session.refresh(obj_USER_ROLE_ADMIN)
		db.session.refresh(obj_USER_ROLE_USER)
		db.session.refresh(obj_USER_ROLE_COMPANY)

		db.session.add(UserRoleScope(obj_USER_ROLE_USER, obj_SCOPE_GET_FEELING_EXTERNAL_UUID))
		db.session.add(UserRoleScope(obj_USER_ROLE_USER, obj_SCOPE_CREATE_FEELING))
		db.session.add(UserRoleScope(obj_USER_ROLE_USER, obj_SCOPE_DELETE_FEELING_FILE))
		db.session.add(UserRoleScope(obj_USER_ROLE_USER, obj_SCOPE_CREATE_FEELING_FILE))
		db.session.add(UserRoleScope(obj_USER_ROLE_USER, obj_SCOPE_GET_USER))
		db.session.add(UserRoleScope(obj_USER_ROLE_ADMIN, obj_SCOPE_GET_USER))
		db.session.add(UserRoleScope(obj_USER_ROLE_ADMIN, obj_SCOPE_GET_FEELING_EXTERNAL_UUID))
		db.session.add(UserRoleScope(obj_USER_ROLE_ADMIN, obj_SCOPE_GET_ALL_COMPANIES))
		db.session.add(UserRoleScope(obj_USER_ROLE_ADMIN, obj_SCOPE_GET_COMPANY_BY_ID))
		db.session.add(UserRoleScope(obj_USER_ROLE_ADMIN, obj_SCOPE_GET_CONTACT_CHANNELS))
		db.session.add(UserRoleScope(obj_USER_ROLE_ADMIN, obj_SCOPE_CREATE_FEELING))
		db.session.add(UserRoleScope(obj_USER_ROLE_ADMIN, obj_SCOPE_DELETE_FEELING_FILE))
		db.session.add(UserRoleScope(obj_USER_ROLE_ADMIN, obj_SCOPE_CREATE_FEELING_FILE))
		db.session.add(UserRoleScope(obj_USER_ROLE_COMPANY, obj_SCOPE_GET_COMPANY_BY_ID))
		db.session.add(UserRoleScope(obj_USER_ROLE_COMPANY, obj_SCOPE_GET_FEELING_EXTERNAL_UUID))

		db.session.commit()

		responseObject = {
			'status': 'success',
			'message': 'Defaults created'
		}
		return make_response(jsonify(responseObject)), 201



defaults_view = DefaultsAPI.as_view('defaults_api')



defaults_blueprint.add_url_rule('/defaults', view_func=defaults_view, methods=['POST'])
