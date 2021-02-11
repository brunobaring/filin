from flask import current_app, request
from uuid import UUID
from emotion import db
from emotion.models import User, Scope, UserRole, UserRoleScope
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



def has_permission(request, scope_name):
	auth_header = request.headers.get('Authorization')
	auth_token = auth_header.split(" ")[1]
	resp = User.decode_auth_token(auth_token)
	user = User.query.filter_by(id_=resp).first()

	scope = Scope.query.filter_by(name=scope_name).first()

	# user_role_scope = db.session.query(UserRoleScope).filter(Scope.id_.like(int(scope.id_), UserRole.id_.like(int(user.user_role.id_))))
	user_role_scope = UserRoleScope.query.filter_by(scope=scope).filter_by(user_role=user.user_role).first()
	return user




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
