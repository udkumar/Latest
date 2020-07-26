import os
import sys
import uuid
import datetime
import json
import logging
import traceback

import flask
from flask import Flask, request, session, redirect, jsonify, make_response, send_from_directory
from flask_paginate import Pagination, get_page_parameter
from flask_cors import CORS, cross_origin
from flask_mail import Mail, Message

from unicodedata import normalize
import uuid
import pdb # for development : pdb.set_trace()

import requests
import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_values
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from functools import wraps
import random

from configs.config import get_db, close_db

logging.basicConfig(filename='logs/maiic_api_logs.log', format='%(asctime)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
logging.basicConfig(level=logging.DEBUG)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app = Flask(__name__)
CORS(app)
mail = Mail(app) # instantiate the mail class 
   
# configuration of mail 
app.config['SECRET_KEY'] = "MAIIC"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024

app.config['MAIL_SERVER']='smtpout.secureserver.net'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'enquiry@maiiceducation.com'
app.config['MAIL_PASSWORD'] = 'Enquiry@123'
app.config['MAIL_DEFAULT_SENDER'] =('MAIIC.Edu.IT','enquiry@maiiceducation.com')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

PREFIX = "/v1"
be_ui_url = os.getenv("MAIIC_UI_URL")
be_api_url = os.getenv("MAIIC_API_URL")

def token_required(f):
	@wraps(f)
	def decorator(*args, **kwargs):
		token = None
		if 'x-access-token' in request.headers:
			token = request.headers['x-access-token']
		if not token:
			return jsonify({"message":"Token is missing!"}), 401
		try:
			data = jwt.decode(token, app.config['SECRET_KEY'])
			connection = get_db()
			cursor = connection.cursor()
			cursor.execute("select u.public_id, r.role_name from users as u, roles as r where u.public_id=%s and u.role_id=r.role_id",(data['public_id'],))
			current_user = cursor.fetchone()
		except:
			traceback.print_exc()
			return jsonify({"message":"Token is invalid!"}), 401
		return f(current_user, *args, **kwargs)
	return decorator

@app.route(PREFIX +'/index', methods=['GET'])
@app.route(PREFIX +'/', methods=['GET'])
def index():
	api_key = validate_api(request)
	if api_key == 'MAIIC':
		return jsonify({"message": "OK: Your api_key is Authorized to access MAIIC APIs"}), 200
	else:
		return jsonify({"message": "ERROR: Unauthorized, api_key is invalid"}), 401

@app.route(PREFIX+"/registration/", methods=['POST'])
@app.route(PREFIX+"/registration", methods=['POST'])
def registration():
	headers = request.headers
	req_from_faculty = headers.get("X-Faculty")
	if req_from_faculty == "userAsFaculty":
		data = request.get_json()
		print(data)
		connection = get_db()
		cursor = connection.cursor()
		
		cursor.execute("select email from users where email=%s",(data['email'],))

		existing_user = cursor.fetchone()
		if existing_user:
			return jsonify({"message" : "A email address already exists."}), 409
		else:
			data['role_id'] = "2"

			auto_user_id = random.randrange(100000,999999)
			auto_user_id = str(auto_user_id)
			print("user_id", auto_user_id)
			auto_password = random.randrange(100000,999999)
			string_pass = str(auto_password)
			print("pass: ",string_pass)
			hashed_password = generate_password_hash(string_pass, method='pbkdf2:sha256')
						
			cursor.execute("INSERT INTO users (public_id, user_id, email, alternet_email, password, first_name, last_name, mobile_number, city, class_std, subject, edu_board, role_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);",(str(uuid.uuid4()), auto_user_id, data['email'], data['alternet_email'], hashed_password, data['firstName'], data['lastName'], data['mobile'], data['city'], data['class_std'], data['subject'], data['edu_board'], data['role_id']))

			connection.commit()
			print("Faculty added...")
		return jsonify({"message" : "Faculty created!"}), 201
	else:
		data = request.get_json()
		print(data)
		connection = get_db()
		cursor = connection.cursor()
		cursor.execute("select email from users where email=%s",(data['email'],))

		existing_user = cursor.fetchone()
		if existing_user:
			return jsonify({"message" : "A email address already exists."}), 409
		else:
			data['role_id'] = "1"

			auto_user_id = random.randrange(100000,999999)
			auto_user_id = str(auto_user_id)
			print("user_id", auto_user_id)

			auto_password = random.randrange(100000,999999)
			string_pass = str(auto_password)
			print("pass: ",string_pass)

			hashed_password = generate_password_hash(string_pass, method='pbkdf2:sha256')

			first_name = data['firstName']
			student_email = data['email']

			cursor.execute("INSERT INTO users (public_id, user_id, email, alternet_email, password, first_name, last_name, mobile_number, city, class_std, subject, edu_board, role_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);",(str(uuid.uuid4()), auto_user_id, data['email'], data['alternet_email'], hashed_password, data['firstName'], data['lastName'], data['mobile'], data['city'], data['class_std'], data['subject'], data['edu_board'], data['role_id']))

			connection.commit()

			# Send email as credential
			msg = Message(subject='MAIIC Login details...', recipients = [student_email])
			msg.html = "Hello <strong>{}</strong>, <p>Your login details are: <br>Student ID = {}, Password = {}</p><br>Click here to login: <a href='http://maiiceducation.com/'>http://maiiceducation.com/</a>".format(first_name, auto_user_id, string_pass)
			mail.send(msg)
			print("user added...")
		return jsonify({"message" : "Student created!"}), 201


@app.route(PREFIX+"/login/", methods=['POST'])
@app.route(PREFIX+"/login", methods=['POST'])
def login():
	data = request.get_json()
	if not data or not data['user_id'] or not data['password']:
		return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic relm="Login Required!"'})

	connection = get_db()
	cursor = connection.cursor()
	cursor.execute("select u.public_id, u.password, r.role_name from users as u, roles as r where u.user_id=%s and u.role_id=r.role_id",(data['user_id'],))
	user = cursor.fetchone()
	if not user:
		return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic relm="Login Required!"'})

	if check_password_hash(user[1], data['password']):
		token = jwt.encode({'public_id' : user[0], 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=60)}, app.config['SECRET_KEY'])
		return jsonify({'token' : token.decode('UTF-8'), 'role' : user[2]}), 200

	return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic relm="Login Required!"'})

@app.route(PREFIX+"/logout", methods=['DELETE'])
def logout():
	pass

@app.route(PREFIX +'/videos', methods=['GET'])
@token_required
def fetch_file(current_user):
	if request.method == 'GET':
		connection = get_db()
		cursor = connection.cursor()
		cursor.execute("select u_id from users where public_id=%s",(current_user[0],))
		user_id = cursor.fetchone()
		role_name = current_user[1]

		cursor.execute("SELECT Videos",(user_id,))
		rows = cursor.fetchall()

		resp = jsonify({'sources' : rows, 'languages' : languages})
		resp.status_code = 201
		return resp
		close_db()

@app.route(PREFIX +'/videos', methods=['POST'])
@token_required
def upload_file(current_user):
	if request.method == 'POST':
		# logger.info("---------------------- File upload api ----------------------")
		# try:	
		pdb.set_trace()	

		videoFileName = ""

		subject = request.form.get('subject')
		chapter = request.form.get('chapter')
		video_url = request.form.get('video_url')
		# video_status = request.form.get('video_status')
		class_standard = request.form.get('class_standard')


		videoFilePath = ""
		videoFileType = ""
		if 'selectFile' in request.files:
			file = request.files['selectFile']
			videoFileType = file.filename.split("/")[-1].split(".")[-1]
			combineDir = UPLOAD_FOLDER+'/'+sourceLang+'/'
			source_directory = str(combineDir)
			os.makedirs(os.path.join(source_directory), exist_ok=True)

		connection = get_db()
		cursor = connection.cursor()

		cursor.execute("select u_id from users where public_id=%s",(current_user[0],))
		userId = cursor.fetchone()
		role_name = current_user[1]

		print("\nuserId:", userId)
		print("\nrole name:", role_name)
		cursor.execute("INSERT INTO videos (file_path, file_type, class_standard, subject, chapter, video_url, u_id) VALUES (%s,%s,%s,%s,%s,%s,%s);", (videoFilePath, videoFileType, class_standard, subject, chapter, video_url, userId))
	

		connection.commit()

		resp = jsonify({'message' : 'File successfully uploaded'})
		resp.status_code = 201
		return resp
		close_db()

@app.route(PREFIX +'/users', methods=['GET'])
@token_required
def fetch_users(current_user):
	pass

if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0', port=3000)
