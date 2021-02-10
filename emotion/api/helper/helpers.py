from flask import current_app
import os



def get_folder_size(feeling_uuid):
	total_size = 0
	start_path = current_app.config['UPLOAD_PATH'] + "/" + str(feeling_uuid)
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
