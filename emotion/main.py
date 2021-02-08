from flask import Blueprint, render_template, Flask, request, redirect, url_for, current_app, make_response
from flask_login import login_required, current_user
import os 

main = Blueprint('main', __name__)

@main.route('/')
def index():
	return render_template('index.html')

@main.route('/profile')
@login_required
def profile():
	return render_template('profile.html', name=current_user.name)

@main.route('/upload', methods=['POST'])
def upload_file():
	uploaded_file = request.files['file']
	for uploaded_file in request.files.getlist('file'):
		filename = uploaded_file.filename
		if filename != '':
			file_ext = os.path.splitext(filename)[1]
			if file_ext not in current_app.config['UPLOAD_EXTENSIONS']:
				abort(400)
			uploaded_file.save(os.path.join(current_app.config['UPLOAD_PATH'], current_user.get_id()))
	return redirect(url_for('main.index'))

# @main.route('/feeling/<int:feeling_id>/file', methods=['POST'])
# def aa(feeling_id):
# 	print("UAU", feeling_id)
# 	return make_response("feeling_id" + str(feeling_id)), 200