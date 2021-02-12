from flask import make_response, jsonify

class HTTPError(Exception):
	
	message = None

	def __init__(self, code, message=None):
		Exception.__init__(self)
		if code == 404:
			self.status = "Not Found"
		elif code == 401:
			self.status = "Unathorized"
		elif code == 400:
			self.status = "Bad Request"
		elif code == 200:
			self.status = "OK"
		elif code == 201:
			self.status = "Created"

		self.code = code

		if message is not None:
			self.message = message


	def to_dict(self, data=None):
		payload = dict()
		if self.message is not None:
			payload['message'] = self.message
		if data is not None:
			payload['data'] = data

		payload['status'] = self.status
		return make_response(jsonify(payload)), self.code


