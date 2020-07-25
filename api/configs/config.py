from configparser import ConfigParser
import psycopg2
from psycopg2 import sql
import os


# absolute_file_path = "/home/uday/WorkStation/PB/pb_works/MAIIC/api/configs/database.ini" 
#absolute_file_path = 'C:/Users/vinod/Desktop/MAIIC Files/Udkumar_code/MAIIC/api/configs/database.ini'
absolute_file_path = os.getenv('DB_CREDENTIALS', '')
def config(filename=absolute_file_path, section='postgresql'):
	parser = ConfigParser()
	parser.read(filename)
 
	db = {}
	if parser.has_section(section):
		params = parser.items(section)
		for param in params:
			db[param[0]] = param[1]
	else:
		raise Exception('Section {0} not found in the {1} file'.format(section, filename))
	return db

def get_db():
	params = config()
	conn = psycopg2.connect(**params)
	return conn

def close_db():
	params = config()
	conn = psycopg2.connect(**params)
	return conn.close()

def validate_api(request):
	headers = request.headers
	api_key = headers.get("X-Api-Key")
	return api_key
