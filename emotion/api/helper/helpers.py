from flask import current_app, request
from uuid import UUID
from emotion import db
from emotion.models import User, Scope, Role, RoleScope, Company, UserCompany
from emotion.api.views.http_error import HTTPError
import os



def get_folder_size(internal_uuid):
	total_size = 0
	start_path = current_app.config['UPLOAD_PATH'] + "/" + str(internal_uuid)
	for dirpath, dirnames, filenames in os.walk(start_path):
		for f in filenames:
			fp = os.path.join(dirpath, f)
			# skip if it is symbolic link
			if not os.path.islink(fp):
				total_size += os.path.getsize(fp)

	return total_size



def save_file(feeling, file, feeling_file):
	folder = os.path.join(current_app.config['UPLOAD_PATH'], str(feeling.id_))

	try:
		os.mkdir(folder)
	except OSError:
		print ("Creation of the directory %s failed" % folder)
	else:
		print ("Successfully created the directory %s " % folder)

	if not os.path.exists(folder):
	    os.makedirs(folder)

	file.save(os.path.join(folder, str(feeling_file.uuid)))



def has_apikey(request):
	auth_key_header = request.headers.get('Authorization-Key')
	if auth_key_header is None:
		return HTTPError(401, 'Missing Authorization-Key header').to_dict()
	auth_key_header = auth_key_header.split(" ")
	if len(auth_key_header) <= 1 or auth_key_header[0] != 'Key' or auth_key_header[1] is None:
		return HTTPError(401, 'Key header malformed').to_dict()

	auth_key_token = auth_key_header[1]
	company = Company.query.filter_by(apikey=auth_key_token).first()
	if company is None:
		return HTTPError(403, 'Access denied.').to_dict()

	return company

def check_apikey(request, user):
	auth_key_header = request.headers.get('Authorization-Key')
	if auth_key_header is None:
		return HTTPError(401, 'Missing Authorization-Key header').to_dict()
	auth_key_header = auth_key_header.split(" ")
	if len(auth_key_header) <= 1 or auth_key_header[0] != 'Key' or auth_key_header[1] is None:
		return HTTPError(401, 'Key header malformed').to_dict()

	auth_key_token = auth_key_header[1]
	company = Company.query.filter_by(apikey=auth_key_token)
	if company is None:
		return HTTPError(403, 'Access denied.').to_dict()

	user_company = UserCompany.query.filter_by(company_id=company.id_).filter_by(user_id=user.id_).first()
	if user_company is None:
		return HTTPError(403, 'Access denied. Can\'t access other companies').to_dict()

	return company



# https://stackoverflow.com/questions/19989481/how-to-determine-if-a-string-is-a-valid-v4-uuid
def is_valid_uuid(uuid_to_test, version=4):
    """
    Check if uuid_to_test is a valid UUID.
    
     Parameters
    ----------
    uuid_to_test : str
    version : {1, 2, 3, 4}
    
     Returns
    -------
    `True` if uuid_to_test is a valid UUID, otherwise `False`.
    
     Examples
    --------
    >>> is_valid_uuid('c9bf9e57-1685-4c89-bafb-ff5af830be8a')
    True
    >>> is_valid_uuid('c9bf9e58')
    False
    """
    
    try:
        uuid_obj = UUID(uuid_to_test, version=version)
    except ValueError:
        return False
    return str(uuid_obj) == uuid_to_test
